# wxcloudrun/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import User


class CloudbaseAuthMiddleware(MiddlewareMixin):
    """
    微信云托管身份认证中间件
    
    从请求头中获取云开发自动注入的用户信息：
    - X-WX-OPENID: 用户的 openid（云开发自动注入）
    - X-WX-UNIONID: 用户的 unionid（如果有）
    - X-WX-APPID: 小程序的 appid
    
    开发和生产环境都使用云托管，无需区分模式
    """
    
    def process_request(self, request):
        # 从请求头获取 openid（云开发自动注入）
        openid = request.headers.get('X-WX-OPENID')
        
        # 调试日志
        print(f"CloudbaseAuthMiddleware: openid={openid}")
        print(f"CloudbaseAuthMiddleware: path={request.path}")
        print(f"CloudbaseAuthMiddleware: headers={dict(request.headers)}")
        
        if openid:
            try:
                # 根据 openid 获取用户
                user = User.objects.get(wechat_openid=openid)
                # 标记用户为已认证（云托管自动认证）
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                request.user = user
                print(f"CloudbaseAuthMiddleware: 用户认证成功 user={user.username}")
            except User.DoesNotExist:
                # 用户不存在，设置为匿名用户
                # 登录接口会创建新用户
                request.user = AnonymousUser()
                print(f"CloudbaseAuthMiddleware: 用户不存在 openid={openid}")
        else:
            # 没有 openid，设置为匿名用户
            request.user = AnonymousUser()
            print(f"CloudbaseAuthMiddleware: 没有 openid")
        
        return None
