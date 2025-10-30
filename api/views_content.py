from rest_framework import viewsets, permissions
from .models import HeroSection, HomeBanner, Location, Promo, AboutSection, BlogPost
from .serializers_content import (
    HeroSectionSerializer, HomeBannerSerializer, LocationSerializer,
    PromoSerializer, AboutSerializer, BlogSerializer
)

class IsStaffOrAbove(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ["staff", "supervisor", "owner", "superuser"]
        )

class HeroSectionViewSet(viewsets.ModelViewSet):
    queryset = HeroSection.objects.all()
    serializer_class = HeroSectionSerializer
    permission_classes = [IsStaffOrAbove]

class BannerViewSet(viewsets.ModelViewSet):
    queryset = HomeBanner.objects.all()
    serializer_class = HomeBannerSerializer
    permission_classes = [IsStaffOrAbove]

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsStaffOrAbove]

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [IsStaffOrAbove]

class AboutViewSet(viewsets.ModelViewSet):
    queryset = AboutSection.objects.all()
    serializer_class = AboutSerializer
    permission_classes = [IsStaffOrAbove]

class BlogViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsStaffOrAbove]
