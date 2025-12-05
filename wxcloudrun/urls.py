"""wxcloudrun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from wxcloudrun import views
from wxcloudrun.api_views import (
    wechat_login,
    UserViewSet,
    ProductCategoryViewSet,
    SpeciesViewSet,
    GeneTagViewSet,
    ProductViewSet,
    OrderViewSet,
    ChatMessageViewSet,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"categories", ProductCategoryViewSet, basename="category")
router.register(r"species", SpeciesViewSet, basename="species")
router.register(r"gene-tags", GeneTagViewSet, basename="gene-tag")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"messages", ChatMessageViewSet, basename="message")

# Swagger/OpenAPI Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="PetBao API",
        default_version="v1",
        description="PetBao 宠物交易平台 API 文档"
    ),
    public=True,
    permission_classes=[],
)

urlpatterns = [
    # API Documentation (Swagger)
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    # API routes
    path("api/auth/wechat-login/", wechat_login, name="wechat-login"),
    path("api/", include(router.urls)),
    # Legacy routes
    path("", views.index, name="index"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
