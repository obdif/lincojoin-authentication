from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('login/', LoginUser.as_view(), name='login'),
    # path('profile/', TestAuthenticaion.as_view(), name='granted'),
    path('reset-password/', ResetPassword.as_view(), name='reset-password'),
    path('password-reset-confirm/<uidb64>/<token>/', ConfirmResetPassword.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('LogOutUser/', LogOutUser.as_view(), name='LogOutUser'),
    
]
