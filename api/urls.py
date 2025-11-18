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

# 🩷 Queue System
from .views_queue import (
    QueueViewSet, 
    join_queue, 
    serve_patient, 
    get_reports, 
    clear_queue
)

# 🩺 Patient System
from .views_patient import (
    PatientViewSet,
    AppointmentViewSet,
    NotificationViewSet,
    BusinessDayViewSet,
)

# 🌐 Google Login
from .views_auth_patient import GoogleLoginView, PatientRegisterView


# --- ROUTER CONFIG ---
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
router.register(r'queue', QueueViewSet, basename='queue')
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'business-days', BusinessDayViewSet, basename='business-days')


# --- URL PATTERNS ---
urlpatterns = [
    # ------------------------------
    # FIRST — Custom Queue Endpoints
    # ------------------------------
    path("queue-join/", join_queue, name='join-queue'),
    path("queue/serve/<int:pk>/", serve_patient),
    path("queue/reports/", get_reports, name="queue-reports"),
    path("queue/clear/", clear_queue),

    # ------------------------------
    # Auth & Profile Endpoints
    # ------------------------------
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/register/', PatientRegisterView.as_view(), name='patient-register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),

    # ------------------------------
    # LAST — Include Router
    # ------------------------------
    path('', include(router.urls)),
]
