from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer


# 🧠 For managing all users (superusers/owners only)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# 👩‍⚕️ For staff — get their own profile
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """
    Returns details of the currently logged-in user.
    This allows all staff to view their profile.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

def perform_create(self, serializer):
    request_user = self.request.user

    # 🛡️ Only superusers or owners can assign roles above "staff"
    if not request_user.is_superuser and serializer.validated_data.get("role") in ["owner", "supervisor", "superuser"]:
        raise PermissionDenied("You are not allowed to assign this role.")

    serializer.save()

