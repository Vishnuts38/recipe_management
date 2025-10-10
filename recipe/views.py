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
    
