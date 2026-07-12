from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer

User = get_user_model()


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    body: { "email": "...", "password": "..." }
    Uses the default SimpleJWT serializer, which already authenticates
    against USERNAME_FIELD = "email" on our custom User model.
    """

    throttle_scope = "auth"


class MeView(RetrieveAPIView):
    """GET /api/v1/auth/me/  -> returns the currently authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
