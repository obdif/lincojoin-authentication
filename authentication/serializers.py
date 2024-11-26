from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import *
from rest_framework_simplejwt.tokens import RefreshToken, Token



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, min_length=7, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password']
        
    def validate(self, attrs):
        password = attrs.get('password', '')
        
        if len(password) <=7:
            raise serializers.ValidationError('Password must be more than 7 characters long.')
        
        return attrs
    
    
    def validate_username(self, value):
        if not value.startswith('@'):
            value = f"@{value}"
        return value
    
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(
            email = validated_data['email'],
            username = validated_data['username'],
            password = password,
        )
        return user
    
 
    
class VerifyEmailSerializer(serializers.ModelSerializer):
    otpcode = serializers.CharField(max_length=6)
    
    class Meta:
        model = CustomUser 
        fields = ['otpcode']
        
    def validate(self, attrs):
        otpcode = attrs.get('otpcode')
        return super().validate(attrs)
    

class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    
    # class Meta:
    #     # model = CustomUser
    #     fields = []
        
    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')
        request = self.context.get('request')

        # Determine if input is email or username
        if '@' in email_or_username:
            user = CustomUser.objects.filter(email=email_or_username).first()
        else:
            # Ensure username starts with '@' as per your format
            if not email_or_username.startswith('@'):
                email_or_username = f'@{email_or_username}'
            user = CustomUser.objects.filter(username=email_or_username).first()
        
        # If user is not found, raise an authentication error
        if not user:
            raise AuthenticationFailed("User not found. Check email/username and try again.")
        
        # Authenticate the user using their email and password
        auth_user = authenticate(request, email=user.email, password=password)
        
        if not auth_user:
            raise AuthenticationFailed("Invalid password! Try again")
            
        if not auth_user.is_verified:
            raise AuthenticationFailed("Email not verified")
        
        # Fetch user tokens if authenticated successfully
        user_tokens = auth_user.token()
        
        return {
            'email': auth_user.email,
            'username': auth_user.username,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
        }





class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    class Meta:
        fields = ['email']
        
    def validate(self, attrs):
        email = attrs.get('email')
        if CustomUser.objects.filter(email = email).exists():
            user = CustomUser.objects.get(email = email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            site_domain = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink = f"http://{site_domain}{relative_link}"
            email_body = f"Hi use the link below to reset your password \n {abslink}"
            data={
                'email_body':email_body,
                'email_subject':"RESET YOUR PASSWORD",
                'to_email': user.email
            }
            send_normal_email(data)
        return super().validate(attrs)
    
    
    
    
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, min_length=7, write_only=True)
    confirm_password = serializers.CharField(max_length=255, min_length=7, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    
    class Meta:
        fields =  ['password', 'confirm_password', 'uidb64', 'token']
    
    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Password Reset link is invalid or has expired", 401)

            # Check if passwords match
            if password != confirm_password:
                raise serializers.ValidationError("Passwords do not match")

            user.set_password(password)
            user.save()
            return user

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        except Exception as e:
            raise AuthenticationFailed("Link is invalid or expired")




class LogOutUserSerializer(serializers.Serializer):
    refresh_token =serializers.CharField()
    
    default_error_messages={
        'bad_token': ("Token is Invalid or has expired")
    }
    
    def validate(self, attrs):
        self.token=attrs.get('refresh_token')
        return attrs
    
    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')