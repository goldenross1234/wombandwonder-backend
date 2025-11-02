# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# 🧩 Core CMS ViewSets
from .views import (
    ServiceViewSet,
    LocationViewSet,
    PromoViewSet,
    HomeBannerViewSet,
    HeroSectionViewSet,
    AboutPageViewSet,
    BlogPostViewSet,
    ServiceCategoryViewSet,
    AboutSectionViewSet,
)

# 👥 User Management & Auth
from .views_user import UserViewSet
from .views_auth import CustomTokenObtainPairView
from .views_profile import MyProfileView

# 🩺 Patient Management (new module)
from .views_patient import (
    PatientViewSet,
    AppointmentViewSet,
    NotificationViewSet,
    BusinessDayViewSet,
)

# --- ROUTER CONFIG ---
router = DefaultRouter()

# 🧱 CMS routes
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

# 🩷 Patient System routes
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'business-days', BusinessDayViewSet, basename='business-days')


# --- URL Patterns ---
urlpatterns = [
    path('', include(router.urls)),

    # ✅ Custom login using JWT
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # JWT refresh & profile
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),
]
