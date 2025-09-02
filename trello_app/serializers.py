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

class CommentDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()

    class Meta:
        model = Comment
        fields = ['user', 'comment_text', 'created_at']

class TaskImageSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)
    class Meta:
        model = TaskImage
        fields = ['task_image_id', 'tasks_lists_id', 'task_image', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']

class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ['task_attachment_id', 'tasks_lists_id','task_attachment', 'uploaded_at', 'uploaded_by', 'updated_at', 'updated_by']

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
                  'created_at','created_by', 'updated_at','is_completed', 'updated_by','assigned_to','image','attachment','comments','checklist_progress','checklist_items']

    def get_checklist_progress(self, obj):

        print("-------obj------", obj)

        checklist_data = obj.checklist_items or {}

        print("-------checklist_data------", checklist_data)
        checklist_items = checklist_data.get("items", [])

        print("-------a------", checklist_items)

        total_items = len(checklist_items)
        print("--------b-----", total_items)

        completed_items = 0
        for item in checklist_items:
            print("-------c------", item)
            if item.get("done", False):
                
                print("a")
            else:
                completed_items = 1
                print("b")



        print("-----------------------/get_checklist_progress/",completed_items)
        return (completed_items / total_items * 100) if total_items > 0 else 0


    def get_comments(self, obj):
        comments = obj.comments.all()
        return [
            {
                "comment": comment.comment_text,
                "commented_by": comment.user.full_name if comment.user else "Unknown"
            }
            for comment in comments
        ]

class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    task_list = TaskListSerializer()

    class Meta:
        model = Comment
        fields = ['comment_id', 'user','task_list', 'comment_text', 'created_at', 'created_by', 'updated_at', 'updated_by']

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

class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ['date_time', 'Details']