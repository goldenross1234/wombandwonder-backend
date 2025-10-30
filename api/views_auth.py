# api/views_auth.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom login serializer to include role and use proper authentication."""

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password")

        # Call parent validate (to generate tokens)
        data = super().validate(attrs)
        data["username"] = user.username
        data["role"] = getattr(user, "role", None)
        data["user_id"] = user.id

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
