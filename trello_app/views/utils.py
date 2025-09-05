
# Helper Function

from rest_framework.response import Response
from rest_framework import status
import os
import random
from django.core.mail import send_mail
from trello_app.models import Activity

########  AUTHENTICATION  ########

# Generate 6-digit random OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function for Log activity
def activity(user, Details):
    return Activity.objects.create(user=user, Details=Details)

# Send otp to user Email logic
def send_otp_email(user_email, otp):
    subject = "TRELLO App OTP for reset password"
    message = f"Hello from TRELLO Task Management App.\n This is OTP for reset your password: {otp} \n This OTP will Expire in 10 minutes"
    from_email = 'vishalsohaliya25@gmail.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)

# get generate full image path, ex."profile_image": "http://127.0.0.1:8000/media/profiles/20241206_piesUt9.jpg"
def get_profile_image(self, obj):
    request = self.context.get('request')
    if obj.profile_image and request:
        host = request.get_host()
        return f"http://{host}{obj.profile_image.url}"
    return None


########  TASKLIST  ########
# function for get comment and his Full name only.
def get_comments(self, obj):
    comments = obj.comments.all()
    return [{"comment": comment.comment_text, "commented_by": comment.user.full_name if comment.user else "Unknown"} 
                for comment in comments]

# Function for calculate CgeckBoxes prohress by 100%
def get_checklist_progress(self, obj):
    print("-------obj------", obj)
    checklist_data = obj.checklist_items or {}
    checklist_items = checklist_data.get("items", [])

    total_items = len(checklist_items)
    completed_items = sum(1 for item in checklist_items if item.get("done", False))
    return (completed_items / total_items * 100) if total_items > 0 else 0

# Function fpr generate full image path, ex."image": "http://127.0.0.1:8000/media/profiles/20241206_piesUt9.jpg"
def get_image(self, obj):
    request = self.context.get('request')
    if obj.image and request:
        host = request.get_host()
        return f"http://{host}{obj.image.url}"
    
# Function for Validate file and images
def validate_media_files(request):
    MAX_ALLOWED_MEDIA_SIZE = 10  # MB
    ALLOWED_EXTENSIONS = [".json", ".pdf", ".xls", ".xlsx", ".csv", ".jpg", ".jpeg", ".png", ".txt"]

    for file in request.FILES.values():
        if file.size > MAX_ALLOWED_MEDIA_SIZE * 1024 * 1024:
            return Response({"status": "fail", "message": f"Please upload {file.name} under size of {MAX_ALLOWED_MEDIA_SIZE}"},status=status.HTTP_400_BAD_REQUEST)

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response({"status": "fail", "message": f"File {file.name} has invalid file type: {ext}"},status=status.HTTP_400_BAD_REQUEST)
