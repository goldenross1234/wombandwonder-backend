# api/urls.py
print("✅ api.urls LOADED")

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
from .views_queue import QueueViewSet, join_queue


# 🩺 Patient Management (new module)
from .views_patient import (
    PatientViewSet,
    AppointmentViewSet,
    NotificationViewSet,
    BusinessDayViewSet,
)

# 🌐 Patient Authentication (Google & Register)
from .views_auth_patient import GoogleLoginView, PatientRegisterView


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
router.register(r'queue', QueueViewSet, basename='queue')

# 🩷 Patient System routes
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'business-days', BusinessDayViewSet, basename='business-days')


# --- URL Patterns ---
urlpatterns = [
    # All registered routes
    path('', include(router.urls)),

    # ✅ Custom login using JWT
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # ✅ Google login & patient registration
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/register/', PatientRegisterView.as_view(), name='patient-register'),

    # ✅ JWT refresh & profile
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),
    
    # ✅ Queue join route
    path("queue-join/", join_queue, name='join-queue'),
]
