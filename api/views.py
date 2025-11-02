# api/views.py
from rest_framework import viewsets, permissions
from .permissions import IsStaffOrAbove
from .models import Service, Location, Promo, HomeBanner, HeroSection, AboutPage, BlogPost, ServiceCategory, AboutSection, Patient
from .serializers import (
    ServiceSerializer, 
    LocationSerializer, 
    PromoSerializer,
    HomeBannerSerializer, 
    HeroSectionSerializer, 
    AboutPageSerializer, 
    BlogPostSerializer, 
    ServiceCategorySerializer, 
    AboutSectionSerializer,
    PatientSerializer
)
from rest_framework.permissions import AllowAny


# 🩷 SERVICES (CRUD - Staff only)
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# 📍 LOCATIONS (CRUD - Staff only)
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsStaffOrAbove]


# 🎁 PROMOS (Public GET, Staff edit)
class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return [permissions.AllowAny()]
        return [IsStaffOrAbove()]


# 🖼️ HOME BANNERS (Public GET, Staff edit)
# 🖼️ BANNERS (Public GET, Staff edit)
class HomeBannerViewSet(viewsets.ModelViewSet):
    queryset = HomeBanner.objects.all().order_by("order")
    serializer_class = HomeBannerSerializer
    permission_classes = [permissions.AllowAny]  # public view, staff edit

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsStaffOrAbove()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)



# 💖 HERO SECTION (Public GET, Staff edit)
class HeroSectionViewSet(viewsets.ModelViewSet):
    queryset = HeroSection.objects.all()
    serializer_class = HeroSectionSerializer
    permission_classes = [permissions.AllowAny]  # temporarily allow public fetch

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsStaffOrAbove()]
    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # ✅ allow partial update
        return super().update(request, *args, **kwargs)


# 💝 ABOUT PAGE (Public GET, Staff edit)
class AboutPageViewSet(viewsets.ModelViewSet):
    queryset = AboutPage.objects.all()
    serializer_class = AboutPageSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsStaffOrAbove()]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


# 📰 BLOG POSTS (Public GET, Staff edit)
class BlogPostViewSet(viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        user = self.request.user
        # 🩷 Only show published blogs to public users
        if not user.is_authenticated:
            return BlogPost.objects.filter(published=True).order_by("-created_at")
        # 🩷 Authenticated users see all (including drafts)
        return BlogPost.objects.all().order_by("-created_at")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Automatically assign the logged-in user (or none if public)."""
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(author=user)


class AboutSectionViewSet(viewsets.ModelViewSet):
    queryset = AboutSection.objects.all()
    serializer_class = AboutSectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        about_page_id = self.request.data.get("about_page")
        if not about_page_id:
            raise serializers.ValidationError({"detail": "Missing about_page ID"})
        serializer.save()

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)