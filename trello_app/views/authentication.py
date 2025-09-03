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

    if User.objects.filter(username=data.get('username')).exists():
        return Response({"status":"error","message": "Username already Exist."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data.get('email')).exists():
        return Response({"status":"error","message": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():    
            user = User.objects.create_user(
                email=data['email'],
                username=data['username'],
                password=data['password'],
                full_name = data['full_name'],
            )
            activity(user, f"username: {user.username} registered, fullname: {user.full_name}")

            serializer = UserDetailSerializer(user, context={'request': request})
            return Response({"status": "success",
                            "message": "User registered successfully.",
                            "data": serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"status":"error","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Login OTP
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"status":"error","message": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)

    if not user:
        return Response({"status":"error","message": "Invalid credentials or user no exists"}, status=status.HTTP_401_UNAUTHORIZED)

    user_data = {
        "user_id": user.user_id,           # type: ignore
        "username": user.username,
        "full_name": user.full_name,       # type: ignore
    }
    
    if user:
        refresh = RefreshToken.for_user(user)
        activity(user, f"{user.username} logged in.")

        return Response({"status":"Login Successfull","access": str(refresh.access_token), "user": user_data,})
    
    return Response({"status":"error","message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

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
    if not email:
        return Response({"status":"error", "message":"Please Enter Email"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email__iexact=email)
        otp = generate_otp()
        ForgotPasswordOTP.objects.create(user=user, otp=otp)
        send_otp_email(email, otp)
        activity(request.user, f"{request.user.username} requested for password reset.")
        return Response({"status":"success", "message": "OTP sent to your email. Please check your Email box!"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"status":"error", "message": "User not exist"}, status= status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status= status.HTTP_404_NOT_FOUND)

# Reset Password 
@api_view(['POST'])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    new_password = request.data.get("new_password")

    if not email or not otp or not new_password:
        return Response({"status":"error", "message": "email, otp, new_password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        otp_ = ForgotPasswordOTP.objects.filter(user=user, otp=otp, is_used=False).last()

        if not otp_:
            return Response({"status":"error", "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() - otp_.created_at > timedelta(minutes=10):
            return Response({"status":"error", "message":"OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        otp_.is_used = True
        otp_.save()
        activity(request.user, f"{request.user.username} resetted password, username: {user.username}")
        return Response({"status":"success", "message":"Password reset successful"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"status":"error", "message":"Invalid email"}, status= status.HTTP_404_NOT_FOUND)

#############################################################################

# Update Profile
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:    
        get_user_id = request.data.get('user_id')
        if not get_user_id:
            return Response({"status":"error", "message":"Please enter user_id"}, status=status.HTTP_400_BAD_REQUEST)
        
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
                user_get.profile_image = request.FILES.get('profile_image', user_get.profile_image)

            user_get.save()
            activity(request.user, f"{request.user.username} updated his profile: {user_get.username}")
            serializer = UserSerializer(user_get, context={'request': request})
            return Response({"status":"success", "message": "Buyer updated successfully","Updated User Data": serializer.data}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"status":"error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Delete Profile
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({"status":"error", "message": "enter User id please"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not request.user.is_superuser and request.user.user_id != int(user_id):
        return Response({"status":"error", "message": "you can not delete others profile"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(user_id = user_id)
        user.delete()
        activity(request.user, f"{request.user.username} deleted his profile: {user.username}")
        return Response({"status":"success", "message": "User deleted"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"status":"error", "message": "User not found"}, status= status.HTTP_404_NOT_FOUND)

# View All Users
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_view_all_users(request):
    try:
        if not request.user.is_superuser:
            return Response({"status":"error", "message": "You do not have permission to view all users"}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({"status":"error", "message": "No users found matching the results"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(users, many=True, context={'request': request})
        activity(request.user, f"{request.user.username} viewed all users")
        return Response({"status":"success", "Users Data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# view  my profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_my_profile(request):
    user = request.user
    try:
        if not user:
            return Response({"status":"error", "message":"User Not Found or Not Exist!"}, status= status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, context={'request': request})
        activity(request.user, f"{request.user.username} viewed his profile")
        return Response({"status":"success", "Users Data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status":"error", "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Function for Log activity
def activity(user, Details):
    return Activity.objects.create(user=user, Details=Details)

# Show User Activity
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def show_activity(request):
    try:
        user = request.user
        get_admin_board = Board.objects.filter(created_by=user)
        
        if get_admin_board.exists():
            get_members = []

            for board in get_admin_board:
                get_members.extend(board.members.values_list("user_id", flat=True))

            get_members.append(user.user_id)

            activity_record = Activity.objects.filter(user_id__in=get_members).order_by("-date_time")

        else:
            activity_record = Activity.objects.filter(user=user).order_by("-date_time")

        serializer = ActivitySerializer(activity_record, many=True)
        return Response({"status": "success","message": "Activity fetched successfully","data": serializer.data},
                         status=status.HTTP_200_OK)
    
    except Activity.DoesNotExist:
        return Response({"status": "error","message": "No activity found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# Function for comments
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request):
    user = request.user
    data = request.data

    if not data.get('tasklist_id') or not data.get('comment_text'):
        return Response({"status":"error", "message": "Task list and comment text required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task_list = TaskList.objects.get(tasklist_id=data['tasklist_id'])
        comment = Comment.objects.create(
            user=user,
            task_list=task_list,
            comment_text=data['comment_text'],
            created_by=request.user,
            updated_by=request.user
        )

        activity(user, f"{user.full_name} commented on task list: {task_list.tasklist_title}")
        serializer = CommentDetailSerializer(comment)
        return Response({"status": "success", "message": "Comment created successfully", "data": serializer.data}, 
                        status=status.HTTP_201_CREATED)

    except TaskList.DoesNotExist:
        return Response({"status": "error", "message": "task list does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Function for Edit Comments
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_comment(request):

    if not request.data.get('comment_id') or not request.data.get('comment_text'):
        return Response({"status":"error", "message": "Comment ID and comment text required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        comment = Comment.objects.get(comment_id=request.data['comment_id'], user=request.user)
        comment.comment_text = request.data['comment_text']
        comment.save()

        activity(request.user, f"{request.user.full_name} edited a comment on task list: {comment.task_list.tasklist_title}")
        serializer = CommentDetailSerializer(comment)
        return Response({"status": "success", "message": "Comment updated successfully", "data": serializer.data},
                        status=status.HTTP_200_OK)

    except Comment.DoesNotExist:
        return Response({"status": "error", "message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Function for Delete Comments
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request):

    if not request.data.get('comment_id'):
        return Response({"status":"error", "message": "Comment ID required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        comment = Comment.objects.get(comment_id=request.data['comment_id'], user=request.user)
        comment.delete()
        activity(request.user, f"{request.user.full_name} deleted a comment from task list: {comment.task_list.tasklist_title}")

        return Response({"status": "success", "message": "Comment deleted successfully"},
                        status=status.HTTP_200_OK)

    except Comment.DoesNotExist:
        return Response({"status": "error", "message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
