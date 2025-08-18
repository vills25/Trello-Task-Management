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

class TaskListSerializer(serializers.ModelSerializer):
    assigned_to = UserDetailSerializer()
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = TaskList
        fields = ['tasklist_id', 'task_card', 'tasklist_title', 'tasklist_description','priority','label_color','start_date','due_date','created_at','created_by', 'is_completed','updated_at', 'updated_by', 'assigned_to']

class TaskCardSerializer(serializers.ModelSerializer):
    task_lists = TaskListSerializer(many=True, read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = TaskCard
        fields = ['is_starred', 'task_id', 'board', 'title','description','is_completed', 'created_at', 'created_by','updated_at', 'updated_by', 'task_lists']

class BoardSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)
    members = UserDetailSerializer(many=True, read_only=True)
    task_cards = TaskCardSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['board_id', 'title', 'description', 'visibility', 'created_by', 'members', 'created_at', 'updated_at', 'updated_by', 'is_starred','task_cards']

class TaskImageSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)
    class Meta:
        model = TaskImage
        fields = ['task_image_id', 'task_card', 'task_image', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']

class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ['task_attachment_id', 'task_card', 'task_attachment', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']