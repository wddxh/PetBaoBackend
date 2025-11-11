# wxcloudrun/authentication.py
from rest_framework.authentication import BaseAuthentication


class CloudbaseAuthentication(BaseAuthentication):
    """
    云托管认证类
    
    不执行任何认证逻辑，直接使用中间件已经设置好的 request.user
    这样可以让 DRF 使用我们的中间件认证结果
    """
    
    def authenticate(self, request):
        """
        返回 None 表示使用 request.user（由中间件设置）
        不返回 None 会导致 DRF 覆盖 request.user
        """
        # DRF 的 request 是一个包装器，底层的 Django request 在 request._request
        # 直接访问底层 Django request 避免触发 DRF 的认证循环
        django_request = request._request
        
        # 如果用户已经被中间件认证（不是 AnonymousUser）
        if hasattr(django_request, 'user') and django_request.user.is_authenticated:
            # 返回 (user, None) 告诉 DRF 使用这个用户
            # auth 参数设为 None 表示没有额外的认证信息
            return (django_request.user, None)
        
        # 返回 None 表示此认证类不处理，让 DRF 继续使用默认的匿名用户
        return None
