from django.contrib import admin
from .models import *

admin.site.site_header = "Trello Task Management Admin Corner"
admin.site.site_title = "Trello Task Management"
admin.site.index_title = "Trello Admin" 

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_active')
    search_fields = ['username', 'email', 'full_name']

class BoardAdmin(admin.ModelAdmin):
    list_display = ('board_id', 'title', 'visibility', 'created_at')
    search_fields = ['board_id', 'title', 'description']

class TaskListAdmin(admin.ModelAdmin):
    list_display = ('tasklist_id', 'task_card','tasklist_title', 'tasklist_description','assigned_to')
    search_fields = ['tasklist_id', 'task_card__title','tasklist_title', 'tasklist_description','assigned_to__username', 'assigned_to__full_name']

class TaskCardAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'board', 'title', 'is_completed')
    search_fields = ['task_id', 'title', 'description','board__title','is_completed','created_by__username','created_by__full_name','is_starred']

class TaskImageAdmin(admin.ModelAdmin):
    list_display = ('task_image_id', 'task_card', 'task_image')

class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task_attachment_id', 'task_card', 'task_attachment')

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'user', 'Details')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'user', 'task_list', 'comment_text', 'created_at')

admin.site.register(User, UserAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(TaskList,TaskListAdmin)
admin.site.register(TaskCard, TaskCardAdmin)
admin.site.register(TaskAttachment,TaskAttachmentAdmin)
admin.site.register(TaskImage,TaskImageAdmin )
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Comment, CommentAdmin)