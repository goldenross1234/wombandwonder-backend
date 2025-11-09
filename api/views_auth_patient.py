# api/views_auth_patient.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from api.models import Patient
from django.conf import settings

User = get_user_model()


class GoogleLoginView(APIView):
    """
    Verify Google token, create user if not exists, then issue JWT.
    """
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Missing token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify Google token
            google_user = id_token.verify_oauth2_token(
                token, requests.Request(), 
                "<YOUR_GOOGLE_CLIENT_ID>"
            )

            email = google_user["email"]
            full_name = google_user.get("name", "")
            sub = google_user["sub"]

            # Check if user exists
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email.split("@")[0],
                    "is_active": True,
                }
            )

            # Ensure they have a Patient profile
            Patient.objects.get_or_create(
                user=user,
                defaults={"full_name": full_name}
            )

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username,
                "email": user.email,
                "new_user": created
            })

        except ValueError:
            return Response({"error": "Invalid or expired Google token"}, status=status.HTTP_400_BAD_REQUEST)


class PatientRegisterView(APIView):
    """
    Manual email signup for patients.
    """
    def post(self, request):
        data = request.data
        email = data.get("email")
        username = data.get("username") or email.split("@")[0]
        password = data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.save()

        Patient.objects.create(user=user, full_name=data.get("full_name", username))

        refresh = RefreshToken.for_user(user)
        return Response({
            "success": True,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username,
            "email": user.email
        })
