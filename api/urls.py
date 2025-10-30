# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ServiceViewSet, LocationViewSet, PromoViewSet, HomeBannerViewSet,
    HeroSectionViewSet, AboutPageViewSet, BlogPostViewSet, 
    ServiceCategoryViewSet, AboutSectionViewSet
)
from .views_user import UserViewSet
from .views_auth import CustomTokenObtainPairView
from .views_profile import MyProfileView

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'service-categories', ServiceCategoryViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'promos', PromoViewSet)
router.register(r'banners', HomeBannerViewSet)
router.register(r'hero', HeroSectionViewSet)
router.register(r'about', AboutPageViewSet, basename='about')
router.register(r'blogs', BlogPostViewSet, basename='blogpost')
router.register(r'sections', AboutSectionViewSet, basename='sections')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),

    # ✅ Only one login endpoint (your custom one)
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),
]
