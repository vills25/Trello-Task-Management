from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'password', 'full_name', 'profile_image','created_at','updated_at']
        extra_kwargs = {'password': {'write_only': True}} # not show password in user detail.

## User Detail Serializer
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'full_name']

class ForgotPasswordOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForgotPasswordOTP
        fields = ['user', 'otp','created_at']

## Comment-Detail Serializer
class CommentDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()

    class Meta:
        model = Comment
        fields = ['user', 'comment_text', 'created_at']

## Task-Image Serializer
class TaskImageSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = TaskImage
        fields = ['task_image_id', 'tasks_lists_id', 'task_image', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']

## Task-Attachment Serializer
class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ['task_attachment_id', 'tasks_lists_id','task_attachment', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']

## Task-List Serializer
class TaskListSerializer(serializers.ModelSerializer):
    assigned_to = UserDetailSerializer()
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField()
    image = TaskImageSerializer(many=True, read_only=True)
    attachment = TaskAttachmentSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    checklist_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskList
        fields = ['tasklist_id', 'task_card', 'tasklist_title', 'tasklist_description','priority','label_color','start_date','due_date',
                  'created_at','created_by', 'updated_at','is_completed', 'updated_by','assigned_to','image','attachment','comments',
                  'checklist_progress','checklist_items']

## Coemment Serializer
class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer() # get user info
    task_list = TaskListSerializer() # get TaskLists

    class Meta:
        model = Comment
        fields = ['comment_id', 'user','task_list', 'comment_text', 'created_at', 'created_by', 'updated_at', 'updated_by']

## Task-Card serializer
class TaskCardSerializer(serializers.ModelSerializer):
    task_lists = TaskListSerializer(many=True, read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = TaskCard
        fields = ['is_starred', 'task_id', 'board', 'title','description','is_completed', 'created_at', 'created_by','updated_at', 'updated_by', 'task_lists']

## Board Serializer
class BoardSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)
    members = UserDetailSerializer(many=True, read_only=True) # get members from UserDetail serializer
    task_cards = TaskCardSerializer(many=True, read_only=True) # get TaskCard here
    
    class Meta:
        model = Board
        fields = ['board_id', 'title', 'description', 'visibility', 'created_by', 'members', 'created_at', 'updated_at', 'updated_by', 'is_starred','task_cards']

## Activity(log) serializer
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['date_time', 'Details']