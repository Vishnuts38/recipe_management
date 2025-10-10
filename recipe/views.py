from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from django.http import JsonResponse
from graphene_django.views import GraphQLView
from rest_framework_simplejwt.authentication import JWTAuthentication



class PrivateGraphQLView(GraphQLView):
    

    def dispatch(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"errors": [{"message": "Authentication token missing"}]}, status=401)

        jwt_auth = JWTAuthentication()

        try:

            token = auth_header.split(" ")[1]
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            request.user = user  
        except Exception:
 
            return JsonResponse({ "errors": [{"message": "Invalid or expired token"}]}, status=401)
        return super().dispatch(request, *args, **kwargs)




    
class AccessTokenOnlyView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.validated_data
        return Response({"access": token_data["access"]}) 
    
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response    
User = get_user_model()
class CreateSuperUserView(APIView):
    # Only superusers can create another superuser
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "User already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        return Response(
            {
                "message": "Superuser created successfully.",
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )