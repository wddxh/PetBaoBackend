from rest_framework import serializers
from .models import (
    User, ProductCategory, Product, ProductImage, ProductVideo,
    Order, ChatMessage
)


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'phone', 'address', 
                  'wechat_openid', 'created_at', 'updated_at']
        read_only_fields = ['id', 'wechat_openid', 'created_at', 'updated_at']


class ProductCategorySerializer(serializers.ModelSerializer):
    """产品分类序列化器"""
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'sort_order', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    """产品图片序列化器"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'sort_order']


class ProductVideoSerializer(serializers.ModelSerializer):
    """产品视频序列化器"""
    class Meta:
        model = ProductVideo
        fields = ['id', 'video_url', 'thumbnail_url', 'sort_order']


class ProductListSerializer(serializers.ModelSerializer):
    """产品列表序列化器（简略信息）"""
    seller_name = serializers.CharField(source='seller.nickname', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    first_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'species', 'morph', 'price', 'status', 
                  'seller_name', 'category_name', 'first_image', 'view_count',
                  'created_at']
    
    def get_first_image(self, obj):
        first_image = obj.images.first()
        return first_image.image_url if first_image else None


class ProductDetailSerializer(serializers.ModelSerializer):
    """产品详情序列化器（完整信息）"""
    seller = UserSerializer(read_only=True)
    category = ProductCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'seller', 'category', 'title', 'description', 
                  'species', 'morph', 'age', 'sex', 'price', 'status',
                  'images', 'videos', 'view_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'seller', 'view_count', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    """产品创建序列化器"""
    images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )
    videos = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['title', 'description', 'species', 'morph', 'age', 'sex', 
                  'price', 'category', 'images', 'videos']
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        videos_data = validated_data.pop('videos', [])
        
        # Create product
        product = Product.objects.create(**validated_data)
        
        # Create images
        for idx, image_url in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image_url=image_url,
                sort_order=idx
            )
        
        # Create videos
        for idx, video_url in enumerate(videos_data):
            ProductVideo.objects.create(
                product=product,
                video_url=video_url,
                sort_order=idx
            )
        
        return product


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器"""
    buyer_name = serializers.CharField(source='buyer.nickname', read_only=True)
    seller_name = serializers.CharField(source='seller.nickname', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_no', 'buyer_name', 'seller_name', 'product_title',
                  'product_image', 'total_amount', 'status', 'created_at']
    
    def get_product_image(self, obj):
        if obj.product:
            first_image = obj.product.images.first()
            return first_image.image_url if first_image else None
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    """订单详情序列化器"""
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_no', 'buyer', 'seller', 'product', 'total_amount',
                  'status', 'receiver_name', 'receiver_phone', 'receiver_address',
                  'shipping_company', 'shipping_no', 'shipped_at', 'payment_method',
                  'paid_at', 'completed_at', 'buyer_note', 'seller_note',
                  'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """订单创建序列化器"""
    class Meta:
        model = Order
        fields = ['product', 'receiver_name', 'receiver_phone', 'receiver_address', 'buyer_note']
    
    def create(self, validated_data):
        product = validated_data['product']
        
        # Generate order number
        import time
        order_no = f"PB{int(time.time() * 1000)}"
        
        # Create order
        order = Order.objects.create(
            order_no=order_no,
            seller=product.seller,
            total_amount=product.price,
            **validated_data
        )
        
        return order


class ChatMessageSerializer(serializers.ModelSerializer):
    """聊天消息序列化器"""
    sender_name = serializers.CharField(source='sender.nickname', read_only=True)
    sender_avatar = serializers.CharField(source='sender.avatar', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'order', 'sender', 'sender_name', 'sender_avatar',
                  'receiver', 'message_type', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']
