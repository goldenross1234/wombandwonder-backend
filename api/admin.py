from django.contrib import admin as django_admin  # ✅ aliased to avoid confusion
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from wombwonder.admin_site import custom_admin_site
from .models import (
    Service,
    Location,
    Promo,
    HomeBanner,
    HeroSection,
    AboutPage,
    AboutSection,
    BlogPost,
)

User = get_user_model()

# --- Service ---
class ServiceAdmin(django_admin.ModelAdmin):
    list_display = ("name", "category", "price", "active")
    search_fields = ("name", "category")


# --- Locations ---
class LocationAdmin(django_admin.ModelAdmin):
    list_display = ("name", "address", "contact", "hours")
    search_fields = ("name",)


# --- Promos ---
class PromoAdmin(django_admin.ModelAdmin):
    list_display = ("title", "discount", "start_date", "end_date")
    search_fields = ("title",)


# --- Home Banner ---
class HomeBannerAdmin(SortableAdminMixin, django_admin.ModelAdmin):
    list_display = ("title", "active", "order", "created_at")
    list_editable = ("active",)
    search_fields = ("title",)


# --- Hero Section ---
class HeroSectionAdmin(django_admin.ModelAdmin):
    list_display = ("title", "active", "image_preview")
    readonly_fields = ("image_preview",)
    fields = ("title", "subtitle", "button_text", "image", "image_preview", "active")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 10px; margin-top: 10px;" />',
                obj.image.url,
            )
        return "(No image uploaded)"
    image_preview.short_description = "Current Image Preview"


# --- Custom User ---
class CustomUserAdmin(django_admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser", "role")
    search_fields = ("username", "email")
    ordering = ("username",)
    fieldsets = (
        ("Login Info", {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("email",)}),
        ("Roles & Permissions", {
            "fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "is_staff", "is_superuser"),
        }),
    )


# --- About Page & Sections ---
class AboutSectionInline(SortableTabularInline):
    model = AboutSection
    extra = 1
    fields = ("title", "content", "image", "active", "order")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:100px; border-radius:8px; margin-top:5px;" />',
                obj.image.url
            )
        return "(No image uploaded)"
    image_preview.short_description = "Preview"


class AboutPageAdmin(SortableAdminMixin, django_admin.ModelAdmin):
    list_display = ("title", "last_updated")
    search_fields = ("title", "content")
    readonly_fields = ("image_preview",)
    fields = ("title", "content", "image", "image_preview", "slug")
    inlines = [AboutSectionInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px; border-radius:8px;" />',
                obj.image.url,
            )
        return "(No image)"
    image_preview.short_description = "Preview"


# --- ✅ Blog Post Admin ---
class BlogPostAdmin(django_admin.ModelAdmin):  # ✅ FIXED: use django_admin, not admin
    list_display = ("title", "author", "published", "created_at")
    list_filter = ("published", "created_at")
    search_fields = ("title", "content")
    readonly_fields = ("slug", "cover_preview")

    fieldsets = (
        (None, {
            "fields": ("title", "slug", "author", "content", "cover_image", "cover_preview", "video_url", "published"),
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 120px; border-radius: 8px;" />',
                obj.cover_image.url,
            )
        return "(No cover image)"
    cover_preview.short_description = "Preview"


# --- Register everything manually ---
custom_admin_site.register(Service, ServiceAdmin)
custom_admin_site.register(Location, LocationAdmin)
custom_admin_site.register(Promo, PromoAdmin)
custom_admin_site.register(HomeBanner, HomeBannerAdmin)
custom_admin_site.register(HeroSection, HeroSectionAdmin)
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(AboutPage, AboutPageAdmin)
custom_admin_site.register(BlogPost, BlogPostAdmin)
