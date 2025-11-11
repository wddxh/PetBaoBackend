# wxcloudrun/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import login
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
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        在视图函数执行前处理，此时 AuthenticationMiddleware 已经运行完毕
        我们可以安全地覆盖 request.user
        """
        # 从请求头获取 openid（云开发自动注入）
        openid = request.headers.get('X-WX-OPENID') or request.headers.get('X-Wx-Openid')
        
        # 调试日志
        print(f"CloudbaseAuthMiddleware.process_view: openid={openid}")
        print(f"CloudbaseAuthMiddleware.process_view: path={request.path}")
        print(f"CloudbaseAuthMiddleware.process_view: headers={dict(request.headers)}")
        
        if openid:
            try:
                # 根据 openid 获取用户
                user = User.objects.get(wechat_openid=openid)
                print(f"CloudbaseAuthMiddleware.process_view: 找到已存在用户 user={user.username}")
            except User.DoesNotExist:
                # 用户不存在，自动创建新用户
                print(f"CloudbaseAuthMiddleware.process_view: 用户不存在，自动创建 openid={openid}")
                
                # 获取 unionid（可能为空）
                unionid = request.headers.get('X-WX-UNIONID') or request.headers.get('X-Wx-Unionid', '')
                if not unionid:
                    unionid = None  # 转换为 None 避免唯一约束冲突
                
                # 创建新用户
                user = User.objects.create(
                    username=f'wx_{openid[:10]}',  # 使用 openid 前10位作为用户名
                    wechat_openid=openid,
                    wechat_unionid=unionid,
                    nickname=f'用户{openid[:6]}',  # 默认昵称
                )
                print(f"CloudbaseAuthMiddleware.process_view: 新用户创建成功 user={user.username}")
            
            # 重要：必须设置 backend 属性才能被 Django 认为是已认证用户
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            
            # 覆盖 request.user
            request.user = user
            
            print(f"CloudbaseAuthMiddleware.process_view: 用户认证成功 user={user.username}, is_authenticated={user.is_authenticated}")
        else:
            # 没有 openid
            print(f"CloudbaseAuthMiddleware.process_view: 没有 openid，user={request.user}, is_authenticated={request.user.is_authenticated}")
        
        return None  # 继续处理请求
