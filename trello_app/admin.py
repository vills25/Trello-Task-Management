from django.contrib import admin
from .models import *

admin. site.site_header = "Trello Task Management Admin Corner"

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_active')
    search_fields = ['username']

class BoardAdmin(admin.ModelAdmin):
    list_display = ('board_id', 'title', 'visibility', 'created_at')
    search_fields = ['board_id', 'title', 'description']

class TaskListAdmin(admin.ModelAdmin):
    list_display = ('tasklist_id', 'task_card','tasklist_title', 'tasklist_description')
    search_fields = ['tasklist_id', 'task_card','tasklist_title']

class TaskCardAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'board', 'title', 'is_completed', 'assigned_to')
    search_fields = ['task_id', 'board', 'title','description','is_completed','due_date','created_at', 'created_by','updated_at', 'updated_by', 'assigned_to']

class TaskImageAdmin(admin.ModelAdmin):
    list_display = ('task_image_id', 'task_card')

class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task_attachment_id', 'task_card', 'task_attachment')

admin.site.register(User, UserAdmin)
admin.site.register(ForgotPasswordOTP)
admin.site.register(Board, BoardAdmin)
admin.site.register(TaskList,TaskListAdmin)
admin.site.register(TaskCard, TaskCardAdmin)
admin.site.register(TaskAttachment,TaskAttachmentAdmin)
admin.site.register(TaskImage,TaskImageAdmin )