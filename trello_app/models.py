from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=15)
    full_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    required_field = ['username','email', 'password','full_name']

    def __str__(self):
        return self.username
    
    @property
    def id(self):
        return self.user_id

class ForgotPasswordOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"
    
class Board(models.Model):
    board_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description =  models.TextField(blank=True)
    visibility = models.CharField(max_length = 10, choices=(("private", "Private"), ("public", "Public")), default='private')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_boards")
    members = models.ManyToManyField(User,related_name="board")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name="updated_boards")

    def __str__(self):
        return self.title
    
class TaskCard(models.Model):
    task_id = models.AutoField(primary_key=True)    
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    is_completed = models.CharField(max_length = 10, choices=(("pending", "Pending"), ("doing", "Doing"), ("complated", "Complated")), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='updated_by')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    
    def __str__(self):
        return  self.title
    
class TaskImage(models.Model):
    task_image_id = models.AutoField(primary_key=True)
    task_card = models.ForeignKey(TaskCard, on_delete=models.CASCADE)
    task_image = models.ImageField(upload_to='task_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='image_uploaded_by')
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='image_updated_by')

class TaskAttachment(models.Model):
    task_attachment_id = models.AutoField(primary_key=True)
    task_card = models.ForeignKey(TaskCard, on_delete= models.CASCADE)
    task_attachment = models.FileField(upload_to='task_attachment/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name='attachment_uploaded_by')
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='attachment_updated_by')

