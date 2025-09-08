from django.db import models
from django.contrib.auth.models import AbstractUser

## Model for User Detail (AbstractUser ka use authentication system (login, password hashing, permissions) automatic mil jaye isiliye kiya hei)
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=150)
    email = models.EmailField(max_length=254,unique=True)
    full_name = models.CharField(max_length=100, blank=True) ## Extra field added
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True) ## Extra field added
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS = ['email', 'full_name'] 

    def __str__(self):
        return self.username

## Model for Store OTP and verify (Foreignkey used -->> User)
class ForgotPasswordOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

## Model for manage Board(WorkSpace)  (Foreignkey used -->> User)
class Board(models.Model):
    board_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=10, choices=(("private", "Private"), ("public", "Public"), ("team", "Team")), default='private')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_boards")
    members = models.ManyToManyField(User, related_name="member_boards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="updated_boards")
    is_starred = models.BooleanField(default=False)

    def __str__(self):
        return self.title

## Model for manage TaskCard  (Foreignkey used -->> Board, User)
class TaskCard(models.Model):
    task_id = models.AutoField(primary_key=True)    
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="task_cards")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_completed = models.CharField(max_length=10, choices=(("pending", "Pending"), ("doing", "Doing"), ("completed", "Completed")), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='task_updated_by')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_created_by')
    is_starred = models.BooleanField(default=False)

    def __str__(self):
        return self.title

## Model for manage TaskLists (Foreignkey -->> TaskCard, User)
class TaskList(models.Model):
    PRIORITY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]
    COLOR_CHOICES = [("green", "Green"), ("yellow", "Yellow"), ("orange", "Orange"), ("red", "Red")]
    tasklist_id = models.AutoField(primary_key=True)
    task_card = models.ForeignKey(TaskCard, on_delete=models.CASCADE, related_name="task_lists")
    tasklist_title = models.CharField(max_length=200)
    tasklist_description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, default="low")
    label_color = models.CharField(max_length=20, default="green")
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="list_created_by")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="list_updated_by")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    checklist_items = models.JSONField(default= dict, blank=True)
    images = models.JSONField(default=list, blank=True)  
    attachments = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.tasklist_title


## Model for activity log (Foreignkey used -->> User)
class Activity(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)
    Details = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.user}----{self.date_time}----{self.Details}'

## Model for store Comments  (Foreignkey used -->> TaskList, User)
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name="comments",)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='comment_created_by')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='comment_updated_by')
