from django.shortcuts import render
from .models import *
from .serializers import *
from .utils import *
from rest_framework.response import Response
from rest_framework import status, views, permissions
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import GenericAPIView
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed





class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer
    # permission_classes = [AllowAny]
    
    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            send_code_to_user(user['email'])
            print(user)
            
            return Response({
                'data': user,
                'message': f'Hi \n thanks for signing up.... an OTP has been sent to your email, check to verify your account'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    

   
class VerifyUserEmail(GenericAPIView):
    serializer_class = VerifyEmailSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        otpCode = serializer.validated_data.get('otpcode')
        
        try:
            user_code_obj = OneTimePassword.objects.get(otp = otpCode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message': 'Email Account verified successfully'
                }, status = status.HTTP_200_OK)
            return Response({
                'message': 'User is already verified'
            }, status = status.HTTP_200_OK)
            
        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'Invalid passcode'
            }, status=status.HTTP_400_BAD_REQUEST)


            

class LoginUser(GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
    
    
    
class ResetPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context = {'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'a link has been sent to your email to reset your password'}, status= status.HTTP_200_OK)
    
    
    
class ConfirmResetPassword(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credential is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
        
        except DjangoUnicodeDecodeError:
            return Response({'message': 'token is invalid or has expired'}, status = status.HTTP_401_UNAUTHORIZED)
        
        
        
        
class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)



class ValidateTokenView(APIView):
   
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Return user details if token is valid
        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }, status=200)


class LogOutUser(GenericAPIView):
    serializer_class=LogOutUserSerializer
    permission_classes=[IsAuthenticated]
    
    
    def post(self, request):
        serializer =self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response (status=status.HTTP_204_NO_CONTENT)
    
    
#     # =========== PROFILE SETUP======================
    
    
# class ProfileView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         # Get the authenticated user's profile
#         profile = request.user.profile

#         # Ensure profile picture URL is accessible
#         profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        
#         # Serialize the profile object
#         serializer = ProfileSerializer(profile)

#         # Add the profile picture URL to the serialized data
#         response_data = serializer.data
#         response_data['profile_picture_url'] = profile_picture_url

#         return Response(response_data)
