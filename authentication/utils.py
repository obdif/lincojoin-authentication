import random 
from django.core.mail import EmailMessage
from django.conf import settings
from .models import *




def generateOtp():
    otp=""
    for i in range(6):
        otp +=str(random.randint(0,9))
    return otp



def send_code_to_user(email):
    subject = "ONE TIME PASSCODE FOR EMAIL VERIFICATION"
    otp_code = generateOtp()
    print(otp_code)
    user = CustomUser.objects.get(email=email)
    # current_site = ""
    email_body = f"Hi {user.email} \n Thanks for signing up blah blah blah blah. \n Your OTP: {otp_code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    
    OneTimePassword.objects.create(user=user, otp=otp_code)
    
    send_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
    send_email.send(fail_silently=True)
    
 

def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body = data['email_body'],
        from_email = settings.EMAIL_HOST_USER,
        to = [data['to_email']]
    )
    email.send()