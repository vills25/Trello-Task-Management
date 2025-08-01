from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(ForgotPasswordOTP)
admin.site.register(Board)
admin.site.register(TaskCard)
admin.site.register(TaskAttachment)
admin.site.register(TaskImage)
