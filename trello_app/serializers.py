from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'password', 'full_name', 'profile_image','created_at','updated_at']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'full_name']

class ForgotPasswordOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForgotPasswordOTP
        fields = ['user', 'otp','created_at']

class BoardSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    members = UserDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['board_id', 'title', 'description', 'visibility', 'created_by', 'members', 'created_at', 'updated_at', 'updated_by']

class TaskCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCard
        fields = ['task_id', 'board', 'title','description','is_completed','due_date','created_at', 'created_by','updated_at', 'updated_by', 'assigned_to']

class TaskImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskImage
        fields = ['task_image_id', 'task_card', 'task_image', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['task_attachment_id', 'task_card', 'task_attachment', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']