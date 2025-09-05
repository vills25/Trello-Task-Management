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
from trello_app.serializers import *
import random

# Register User
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data

    # Check if Username or Email Exist before?
    if User.objects.filter(username=data.get('username')).exists():
        return Response({"status":"fail","message": "Username already Taken or Exist."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data.get('email')).exists():
        return Response({"status":"fail","message": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():    
            user = User.objects.create_user(
                email=data['email'],
                username=data['username'],
                password=data['password'],
                full_name = data['full_name'],
            )
            activity(user, f"username: {user.username} registered, fullname: {user.full_name}")

            serializer = UserDetailSerializer(user)
            return Response({"status": "success", "message": "User registered successfully.","User Detail": serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"status":"error","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Login and generate simple JWT token
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"status":"fail","message": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate using Django's built-in authentication
    user = authenticate(username=username, password=password)

    if not user:
        return Response({"status":"fail","message": "Invalid credentials or user no exists"}, status=status.HTTP_401_UNAUTHORIZED)

    user_data = {"user_id": user.user_id, "username": user.username, "full_name": user.full_name,}
    
    if user:
        refresh = RefreshToken.for_user(user)
        activity(user, f"{user.username} logged in.")

        return Response({"status":"Login Successfull", "access_token": str(refresh.access_token) ,"user": user_data,})
    
    return Response({"status":"fail","message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Update Profile
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:    
        get_user_id = request.data.get('user_id')
        if not get_user_id:
            return Response({"status":"fail", "message":"Please enter user_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # fatch user data by get_user_id
        user_get = User.objects.get(user_id=get_user_id)
        request_data = request.data

        # Validate and update each field if present in request
        with transaction.atomic():
            if 'username' in request_data:
                    if User.objects.filter(username=request_data['username']).exclude(pk=user_get.user_id).exists():
                        return Response({"status":"fail", "message": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
                    user_get.username = request_data['username']
            
            if 'email' in request_data:
                if User.objects.filter(email=request_data['email']).exclude(pk=user_get.user_id).exists():
                    return Response({"status":"fail", "message": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
                user_get.email = request_data['email']
            
            if 'password' in request_data:
                user_get.set_password(request_data['password'])
            
            if 'full_name' in request_data:
                user_get.full_name = request_data['full_name']

            # If new image uploaded, else keep old
            if 'profile_image' in request_data:
                user_get.profile_image = request.FILES.get('profile_image', user_get.profile_image)

            user_get.save()

            activity(request.user, f"{request.user.username} updated his profile: {user_get.username}")
            serializer = UserSerializer(user_get, context={'request': request}) 
            return Response({"status":"success", "message": "Buyer updated successfully", "Updated User Data": serializer.data}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"status":"fail", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Delete Profile
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile(request):

    user_id = request.data.get('user_id')

    if not user_id:
        return Response({"status":"fail", "message": "enter User id please"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not request.user.is_superuser and request.user.user_id != user_id:
        return Response({"status":"fail", "message": "you can not delete others profile"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(user_id = user_id)
        user.delete()

        activity(request.user, f"{request.user.username} deleted his profile: {user.username}")
        return Response({"status":"success", "message": "User deleted"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"status":"fail", "message": "User not found"}, status= status.HTTP_404_NOT_FOUND)

###########################################################################

# Generate 6-digit random OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send otp to user Email logic
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

    if not email:
        return Response({"status":"fail", "message":"Please Enter Email"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email__iexact=email)
        otp = generate_otp()
        ForgotPasswordOTP.objects.create(user=user, otp=otp)
        send_otp_email(email, otp)
        activity(request.user, f"{request.user.username} requested for password reset.")
        return Response({"status":"success", "message": "OTP sent to your email. Please check your Email box!"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"status":"fail", "message": "User not exist"}, status= status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status= status.HTTP_404_NOT_FOUND)

# validate otp and Reset Password 
@api_view(['POST'])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    new_password = request.data.get("new_password")

    if not email or not otp or not new_password:
        return Response({"status":"fail", "message": "email, otp, new_password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        # Verify OTP (unused + latest)
        otp_ = ForgotPasswordOTP.objects.filter(user=user, otp=otp, is_used=False).last()

        if not otp_:
            return Response({"status":"fail", "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        # OTP validity check (10 minutes)
        if timezone.now() - otp_.created_at > timedelta(minutes=10):
            return Response({"status":"fail", "message":"OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # Mark OTP as used
        otp_.is_used = True
        otp_.save()
        activity(request.user, f"{request.user.username} resetted password, username: {user.username}")
        return Response({"status":"success", "message":"Password reset successful"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"status":"fail", "message":"Invalid email"}, status= status.HTTP_404_NOT_FOUND)

#############################################################################

# Only Superuser can search all users
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_view_all_users(request):
    try:
        if not request.user.is_superuser:
            return Response({"status":"fail", "message": "You do not have permission to view all users"}, status=status.HTTP_403_FORBIDDEN)

        # Apply filters (if provided)
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
            return Response({"status":"fail", "message": "No users found matching the results"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(users, many=True, context={'request': request})
        activity(request.user, f"{request.user.username} viewed all users")
        return Response({"status":"success", "message":"User detail found" ,"Users Data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# view my profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_my_profile(request):
    user = request.user
    try:
        if not user:
            return Response({"status":"fail", "message":"User Not Found or Not Exist!"}, status= status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, context={'request': request})
        activity(request.user, f"{request.user.username} viewed his profile")
        return Response({"status":"success", "message":"Profile fetched" ,"Users Data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status":"error", "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Function for Log activity
def activity(user, Details):
    return Activity.objects.create(user=user, Details=Details)

# # Show user activity (own + boards they created)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def show_activity(request):
    try:
        user = request.user
        get_admin_board = Board.objects.filter(created_by=user)

         # Collect members of boards created by user
        if get_admin_board.exists():
            get_members = []

            for board in get_admin_board:
                get_members.extend(board.members.values_list("user_id", flat=True))

            get_members.append(user.user_id)
            # Fetch activities of all these users
            activity_record = Activity.objects.filter(user_id__in=get_members).order_by("-date_time")

        else:    # Otherwise, fetch only own activity
            activity_record = Activity.objects.filter(user=user).order_by("-date_time")

        serializer = ActivitySerializer(activity_record, many=True)
        return Response({"status": "success", "message": "Activity fetched successfully","Activity Detail": serializer.data},
                         status=status.HTTP_200_OK)
    
    except Activity.DoesNotExist:
        return Response({"status": "fail","message": "No activity found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
