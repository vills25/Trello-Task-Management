from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from trello_app.models import *
from trello_app.serializers import UserSerializer
import random

# Register User
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data

    if User.objects.filter(username=data.get('username')).exists():
        return Response({"error": "Username already Exist."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data.get('email')).exists():
        return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():    
            user = User.objects.create_user(
                email=data['email'],
                username=data['username'],
                password=data['password'],
                full_name = data['full_name'],
            )
            return Response({"message": "User registered successfully.",
                            "user_id": user.user_id,
                            "email": user.email,
                            "username": user.username,
                            "full_name": user.full_name}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Login OTP
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials or user no exists"}, status=status.HTTP_401_UNAUTHORIZED)

    user_data = {
        "user_id": user.user_id,           # type: ignore
        "username": user.username,
        "full_name": user.full_name,       # type: ignore
    }
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            # "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data,
        })
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

###########################################################################

#Generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send Email
def send_otp_email(user_email, otp):
    subject = "TRELLO App OTP for reset password"
    message = f"Hello from TRELLO Task Management App.\n This is OTP for reset your password: {otp} \n This OTP will Expire in 10 minutes"
    from_email = 'vishalsohaliya25@gmail.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)

# Forgot Password and Send mail
@api_view(['POST'])
def forgot_password_sent_email(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email__iexact=email)
        otp = generate_otp()
        ForgotPasswordOTP.objects.create(user=user, otp=otp)
        send_otp_email(email, otp)
        return Response({"message": "OTP sent to your email. Please check your Email box!"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not exist"}, status= status.HTTP_404_NOT_FOUND)

# Reset Password 
@api_view(['POST'])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    new_password = request.data.get("new_password")

    try:
        user = User.objects.get(email=email)
        otp_ = ForgotPasswordOTP.objects.filter(user=user, otp=otp, is_used=False).last()

        if not otp_:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() - otp_.created_at > timedelta(minutes=10):
            return Response({"OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        otp_.is_used = True
        otp_.save()
        return Response({"Password reset successful"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
 
        return Response({"Invalid email"}, status= status.HTTP_404_NOT_FOUND)

#############################################################################

# Update Profile
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:    
        get_user_id = request.data.get('user_id')
        user_get = User.objects.get(user_id=get_user_id)
        data = request.data
        with transaction.atomic():
            if 'username' in data:
                    if User.objects.filter(username=data['username']).exclude(pk=user_get.user_id).exists():
                        return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
                    user_get.username = data['username']
            
            if 'email' in data:
                if User.objects.filter(email=data['email']).exclude(pk=user_get.user_id).exists():
                    return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
                user_get.email = data['email']
            
            if 'password' in data:
                user_get.set_password(data['password'])
            
            if 'full_name' in data:
                user_get.full_name = data['full_name']

            if 'profile_image' in data:
                    user_get.profile_image = request.FILES.get('profile_pic', user_get.profile_image)    

            user_get.save()

            return Response({
                    "message": "Buyer updated successfully",
                    "buyer_id": user_get.user_id,
                    "username": user_get.username,
                    "full_name": user_get.full_name,
                    "profile_image": user_get.profile_image.url if user_get.profile_image else None,
                    "email": user_get.email
                }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Delete Profile
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({"error": "enter User id please"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(user_id = user_id)
        user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status= status.HTTP_404_NOT_FOUND)

# View All Users
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_view_all_users(request):
    try:
        if not request.user.is_superuser:
            return Response({"error": "You do not have permission to view all users"}, status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username', '')
        email = request.data.get('email', '')
        user_id = request.data.get('user_id', '')
        full_name = request.data.get('full_name', '')

        users = User.objects.all()
        if username:
            users = users.filter(username__icontains=username)
        if email:
            users = users.filter(email__icontains=email)
        if user_id:
            users = users.filter(user_id=user_id)
        if full_name:
            users = users.filter(full_name__icontains=full_name)
        
        if not users.exists():
            return Response({"message": "No users found matching the results"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(users, many=True)
        return Response({"Users Data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# view  my profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_my_profile(request):
    user = request.user
    user_data = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "profile_image": user.profile_image.url if user.profile_image else None
    }
    return Response({"User Data": user_data}, status=status.HTTP_200_OK)