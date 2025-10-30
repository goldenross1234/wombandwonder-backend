# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Service, Location, Promo, HomeBanner, HeroSection, AboutPage, BlogPost, ServiceCategory, User, AboutSection
from django.utils.text import slugify

#User = get_user_model()
from django.conf import settings


# 🩷 SERVICE
class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        source='category',
        write_only=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)  # 🆕 Add this

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',       # full category object
            'category_id',    # writeable ID field
            'category_name',  # flat text for easy frontend use
            'active',
        ]


# 📍 LOCATION
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


# 🎁 PROMO
class PromoSerializer(serializers.ModelSerializer):
    is_active_now = serializers.ReadOnlyField()

    class Meta:
        model = Promo
        fields = "__all__"


# 🖼️ BANNERS
class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True, 'allow_empty_file': True},
        }



# 💖 HERO SECTION
class HeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True, 'allow_empty_file': True},
        }

    def update(self, instance, validated_data):
        # 🧠 Only replace image if a new one is provided
        image = validated_data.get("image", None)
        if image is None:
            validated_data.pop("image", None)
        return super().update(instance, validated_data)


# 💝 ABOUT PAGE

class AboutSectionSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AboutSection
        fields = [
            'id',
            'about_page',   # 👈 include the foreign key
            'title',
            'content',
            'image',
            'active',
            'order',
        ]
        read_only_fields = ['about_page']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

        
class AboutPageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    sections = AboutSectionSerializer(many=True, read_only=True)

    class Meta:
        model = AboutPage
        fields = ['id', 'title', 'content', 'image', 'slug', 'last_updated', 'sections']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


# 📰 BLOG
class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "author",
            "author_name",
            "content",
            "cover_image",
            "video_url",
            "published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "author", "created_at", "updated_at"]

    def create(self, validated_data):
        # Auto-slugify title — ensure unique slug even for same titles
        title = validated_data.get("title", "")
        slug_base = slugify(title)
        slug = slug_base
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1
        validated_data["slug"] = slug
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Allow draft edits without overwriting slug
        title = validated_data.get("title", None)
        if title and title != instance.title:
            slug_base = slugify(title)
            slug = slug_base
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(id=instance.id).exists():
                slug = f"{slug_base}-{counter}"
                counter += 1
            instance.slug = slug

        return super().update(instance, validated_data)


# 👥 USER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "is_active", "is_staff", "is_superuser",
            "last_login", "date_joined"
        ]
        read_only_fields = ["id", "is_active", "is_staff", "is_superuser", "last_login", "date_joined"]
