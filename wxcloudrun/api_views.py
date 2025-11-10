import requests
from datetime import datetime
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.db.models import Q

from .models import (
    User, ProductCategory, Product, ProductImage, ProductVideo,
    Order, ChatMessage
)
from .serializers import (
    UserSerializer, ProductCategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateSerializer, OrderListSerializer,
    OrderDetailSerializer, OrderCreateSerializer, ChatMessageSerializer
)


# WeChat Login
@api_view(['POST'])
@permission_classes([AllowAny])
def wechat_login(request):
    """微信小程序登录 - 云托管模式
    
    云开发会自动注入用户的 openid 到请求头 X-WX-OPENID
    不需要通过 code 换取 session_key
    """
    nickname = request.data.get('nickname', '')
    avatar = request.data.get('avatar', '')
    
    # 从云托管请求头获取 openid
    openid = request.headers.get('X-WX-OPENID')
    unionid = request.headers.get('X-WX-UNIONID', '')
    
    if not openid:
        return Response({'error': '缺少云托管环境信息 (X-WX-OPENID)'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    print(f"云托管登录, openid: {openid}")
    
    try:
        # Get or create user
        user, created = User.objects.get_or_create(
            wechat_openid=openid,
            defaults={
                'username': f'wx_{openid[:10]}',
                'nickname': nickname or f'用户{openid[:6]}',
                'avatar': avatar,
                'wechat_unionid': unionid
            }
        )
        
        # Update user info if not created
        if not created and (nickname or avatar):
            if nickname:
                user.nickname = nickname
            if avatar:
                user.avatar = avatar
            user.save()
        
        # 云托管模式：不需要返回 token
        return Response({
            'user': UserSerializer(user).data
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """更新用户资料"""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Product Category ViewSet
class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """产品分类视图集（只读）"""
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]


# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    """产品视图集"""
    queryset = Product.objects.all()
    
    def get_permissions(self):
        """
        根据不同的操作设置不同的权限
        - list, retrieve: 允许匿名访问（浏览商品）
        - create, update, delete: 需要认证
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filter by category
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by species
        species = self.request.query_params.get('species', None)
        if species:
            queryset = queryset.filter(species__icontains=species)
        
        # Filter by morph
        morph = self.request.query_params.get('morph', None)
        if morph:
            queryset = queryset.filter(morph__icontains=morph)
        
        # Filter by sex
        sex = self.request.query_params.get('sex', None)
        if sex:
            queryset = queryset.filter(sex=sex)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', 'available')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(species__icontains=search) |
                Q(morph__icontains=search)
            )
        
        return queryset.select_related('seller', 'category').prefetch_related('images', 'videos')
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """获取产品详情，增加浏览次数"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """获取我发布的产品"""
        products = self.get_queryset().filter(seller=request.user)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


# Order ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Users can only see orders where they are buyer or seller
        return Order.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('buyer', 'seller', 'product')
    
    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_purchases(self, request):
        """我的购买订单"""
        print(f"my_purchases: user={request.user}, is_authenticated={request.user.is_authenticated}")
        orders = self.get_queryset().filter(buyer=request.user)
        print(f"my_purchases: found {orders.count()} orders")
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_sales(self, request):
        """我的销售订单"""
        print(f"my_sales: user={request.user}, is_authenticated={request.user.is_authenticated}")
        orders = self.get_queryset().filter(seller=request.user)
        print(f"my_sales: found {orders.count()} orders")
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """支付订单"""
        order = self.get_object()
        
        # Verify order belongs to buyer
        if order.buyer != request.user:
            return Response({'error': '无权操作此订单'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'pending_payment':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Integrate with WeChat Pay
        # For now, just update status
        order.status = 'pending_shipment'
        order.paid_at = datetime.now()
        order.payment_method = 'wechat_pay'
        order.save()
        
        # Update product status
        if order.product:
            order.product.status = 'reserved'
            order.product.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """发货"""
        order = self.get_object()
        
        # Verify order belongs to seller
        if order.seller != request.user:
            return Response({'error': '无权操作此订单'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'pending_shipment':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        shipping_company = request.data.get('shipping_company')
        shipping_no = request.data.get('shipping_no')
        
        if not shipping_company or not shipping_no:
            return Response({'error': '请提供物流信息'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'pending_receipt'
        order.shipping_company = shipping_company
        order.shipping_no = shipping_no
        order.shipped_at = datetime.now()
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm_receipt(self, request, pk=None):
        """确认收货"""
        order = self.get_object()
        
        # Verify order belongs to buyer
        if order.buyer != request.user:
            return Response({'error': '无权操作此订单'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'pending_receipt':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'completed'
        order.completed_at = datetime.now()
        order.save()
        
        # Update product status
        if order.product:
            order.product.status = 'sold'
            order.product.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()
        
        # Only buyer can cancel, and only if not paid
        if order.buyer != request.user:
            return Response({'error': '无权操作此订单'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status not in ['pending_payment', 'pending_shipment']:
            return Response({'error': '订单状态不允许取消'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.save()
        
        # Update product status back to available
        if order.product:
            order.product.status = 'available'
            order.product.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


# Chat Message ViewSet
class ChatMessageViewSet(viewsets.ModelViewSet):
    """聊天消息视图集"""
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        order_id = self.request.query_params.get('order', None)
        
        queryset = ChatMessage.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )
        
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        return queryset.select_related('sender', 'receiver', 'order')
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """标记消息为已读"""
        message_ids = request.data.get('message_ids', [])
        ChatMessage.objects.filter(
            id__in=message_ids,
            receiver=request.user
        ).update(is_read=True)
        return Response({'status': 'success'})
