from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


# User Model
class User(AbstractUser):
    """用户表 - 扩展Django默认用户模型"""
    wechat_openid = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='微信OpenID')
    wechat_unionid = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='微信UnionID')
    avatar = models.URLField(max_length=500, null=True, blank=True, verbose_name='头像URL')
    nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='昵称')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='手机号')
    address = models.TextField(null=True, blank=True, verbose_name='地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.nickname or self.username


# Product Categories
class ProductCategory(models.Model):
    """产品分类表"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(null=True, blank=True, verbose_name='分类描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_categories'
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    """产品表"""
    SEX_CHOICES = [
        ('male', '雄性'),
        ('female', '雌性'),
        ('unknown', '未知'),
    ]

    STATUS_CHOICES = [
        ('available', '在售'),
        ('sold', '已售'),
        ('reserved', '已预订'),
        ('offline', '下架'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', verbose_name='卖家')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='分类')
    
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    species = models.CharField(max_length=100, verbose_name='物种')
    morph = models.CharField(max_length=200, null=True, blank=True, verbose_name='品系/基因')
    age = models.CharField(max_length=50, null=True, blank=True, verbose_name='年龄')
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='unknown', verbose_name='性别')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='状态')
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'products'
        verbose_name = '产品'
        verbose_name_plural = '产品'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# Product Images
class ProductImage(models.Model):
    """产品图片表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='产品')
    image_url = models.URLField(max_length=500, verbose_name='图片URL')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_images'
        verbose_name = '产品图片'
        verbose_name_plural = '产品图片'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.product.title} - Image {self.sort_order}"


# Product Videos
class ProductVideo(models.Model):
    """产品视频表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos', verbose_name='产品')
    video_url = models.URLField(max_length=500, verbose_name='视频URL')
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True, verbose_name='缩略图URL')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_videos'
        verbose_name = '产品视频'
        verbose_name_plural = '产品视频'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.product.title} - Video {self.sort_order}"


# Order Model
class Order(models.Model):
    """订单表"""
    STATUS_CHOICES = [
        ('pending_payment', '待支付'),
        ('pending_shipment', '待发货'),
        ('pending_receipt', '待收货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunding', '退款中'),
        ('refunded', '已退款'),
    ]

    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单号')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_buyer', verbose_name='买家')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_seller', verbose_name='卖家')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='产品')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment', verbose_name='订单状态')
    
    # 收货信息
    receiver_name = models.CharField(max_length=100, verbose_name='收货人姓名')
    receiver_phone = models.CharField(max_length=20, verbose_name='收货人电话')
    receiver_address = models.TextField(verbose_name='收货地址')
    
    # 物流信息
    shipping_company = models.CharField(max_length=100, null=True, blank=True, verbose_name='物流公司')
    shipping_no = models.CharField(max_length=100, null=True, blank=True, verbose_name='物流单号')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    
    # 支付信息
    payment_method = models.CharField(max_length=50, null=True, blank=True, verbose_name='支付方式')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    
    # 完成信息
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    # 备注
    buyer_note = models.TextField(null=True, blank=True, verbose_name='买家备注')
    seller_note = models.TextField(null=True, blank=True, verbose_name='卖家备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no


# Chat Message Model (for communication system)
class ChatMessage(models.Model):
    """聊天消息表"""
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('video', '视频'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages', verbose_name='订单')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'chat_messages'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.nickname} -> {self.receiver.nickname}"
