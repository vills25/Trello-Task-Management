from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import User, Board,TaskCard, TaskAttachment, TaskImage
from trello_app.serializers import TaskCardSerializer, TaskAttachmentSerializer, TaskImageSerializer
from django.utils import timezone
from datetime import datetime

# Search Task Cards    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_tasks(request):
    try:    
        data = request.data
        
        task_id = data.get('task_id')
        board = data.get('board','')
        description = data.get('description','')
        due_date= data.get('due_date','')
        created_by= data.get('created_by','')
        is_completed= data.get('is_completed','')
        updated_by= data.get('updated_by','')

        queryset = Board.objects.filter()

        if task_id:
                queryset = queryset.filter(pk=task_id)

        if board:
                queryset = queryset.filter(board__icontains=board)

        if description:
                queryset = queryset.filter(description__icontains=description)

        if due_date:
                queryset = queryset.filter(due_date__icontains=due_date)

        if created_by:
                queryset = queryset.filter(created_by__icontains=created_by)

        if updated_by:
                queryset = queryset.filter(updated_by__icontains=updated_by)

        if is_completed:
                queryset = queryset.filter(is_completed__icontains=is_completed)
        
        if not queryset.exists():
                return Response({"message": "No matching Tasks found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskCardSerializer(queryset, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# View Task Cards
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_get(request):
    task_id = request.data.get("task_id")
    if not task_id:
        return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = TaskCard.objects.get(task_id=task_id)
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
   
    if task.created_by != user:
        return Response({"error": "You can not view otheer tasks."}, status=status.HTTP_403_FORBIDDEN)

    return Response({
                     "Task_id": task.task_id,
                     "Task_title": task.title,
                     "Task_Board": task.board.title,
                     "Description": task.description,
                     "Task_Status": task.is_completed,
                     "Assigned_to":task.assigned_to.full_name if task.assigned_to else "Unassigned",
                     "Created_by": task.created_by.full_name,
                     "Created_at": task.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                     "Updated_by": task.updated_by.full_name if task.updated_by else "None",
                     "Updated_at": task.updated_at.strftime("%d-%m-%Y %H:%M:%S"),
                     }, status=status.HTTP_200_OK)


# Create Task Card
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    user = request.user
    data = request.data
    required_fields = ['title', 'description', 'board_id']

    if not all(field in data and data.get(field) for field in required_fields):
        return Response({"error": "Please fill all required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        try:
            board = Board.objects.get(board_id=data.get("board_id"))
        except Board.DoesNotExist:
            return Response({"error": "Board does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if user not in board.members.all():
            return Response({"error": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        assigned_to_id = data.get("assigned_to")
        assigned_to_user = None
        if assigned_to_id:
            try:
                assigned_to_user = User.objects.get(user_id=assigned_to_id)
            except User.DoesNotExist:
                return Response({"error": "Assigned user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        valid_status = ["pending", "doing", "complated"]
        is_completed = data.get("is_completed", "pending")

        if is_completed not in valid_status:
            return Response({"error": "Invalid task status."},status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            task = TaskCard.objects.create(
                board=board,
                title=data.get("title"),
                description=data.get("description"),
                due_date=data.get("due_date"),
                is_completed=is_completed,
                created_by=user,
                assigned_to=assigned_to_user
            )

            for img in request.FILES.getlist("images"):
                TaskImage.objects.create(task_card=task, task_image=img)

            for file in request.FILES.getlist("attachments"):
                TaskAttachment.objects.create(task_card=task, task_attachment=file)

            return Response({"message": "Task created successfully", "task_id": task.task_id}, status= status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Update Task Card
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_task(request):

    data = request.data
    task_id = data.get("task_id")

    if not task_id:
        return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = TaskCard.objects.get(task_id=task_id)
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user != task.created_by:
        return Response({"error": "You cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)

    task_image = TaskImage.objects.filter(task_card=task).first()
    task_attachment = TaskAttachment.objects.filter(task_card=task).first()

    try:
        with transaction.atomic():   

            if 'title' in data:
                task.title = data['title']
            
            if 'description' in data:
                task.description = data['description']

            if 'due_date' in data:
                task.due_date = data['due_date']    

            if 'assigned_to' in data:
                assigned_to = data["assigned_to"]
                if assigned_to:
                    try:
                        assigned_user_upd = User.objects.get(user_id=assigned_to)
                        task.assigned_to = assigned_user_upd
                    except User.DoesNotExist:
                        return Response({"error": "Assigned user not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    task.assigned_to = None

            if "image" in request.FILES:
                if task_image:
                    task_image. task_image = request.FILES["image"]
                    task_image.save()
                else:
                    TaskImage.objects.create(task=task, image=request.FILES["image"])

            if "attachment" in request.FILES:
                if task_attachment:
                    task_attachment. task_attachment = request.FILES["attachment"]
                    task_attachment.save()
                else:
                    TaskAttachment.objects.create(task=task, file=request.FILES["attachment"])
        
            task.save()
            serializer = TaskCardSerializer(task)
            return Response({"message": "Task updated successfully", "Updated task Details":serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Task Card Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request):

    task_id = request.data.get("task_id")

    if not task_id:
        return Response({"Task ID is Required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        task = TaskCard.objects.get(id=task_id)
        if request.user != task.created_by:
            return Response({"error": "You cannot delete this task"}, status=status.HTTP_403_FORBIDDEN)
        
        task.delete()
        return Response({"message": "Task deleted successfully"}, status= status.HTTP_200_OK)
    
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status= status.HTTP_404_NOT_FOUND)

# Tasks Status
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_task_complete(request):

    task_id = request.data.get("task_id")
    if not task_id:
        return Response({"Task ID is Required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():    
            task = TaskCard.objects.get(task_id=task_id)
            
            if request.user not in task.board.members.all():
                return Response({"error": "You can not change the status of task of others task."}, status=status.HTTP_403_FORBIDDEN)
            
            task_status_update = request.data.get("status")

            if not task_status_update:
                return Response({"error": "Task status is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if task_status_update not in ["pending", "doing", "complated"]:
                return Response({"error": "Invalid task status"}, status=status.HTTP_400_BAD_REQUEST)
            
            if task_status_update == "complated":
                task.is_completed = task_status_update
            
            elif task_status_update == "doing":
                task.is_completed = task_status_update

            elif task_status_update == "pending":
                task.is_completed = task_status_update

            task.save()
            return Response({"message": "Task status Updated"}, status= status.HTTP_200_OK)
        
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"},status= status.HTTP_404_NOT_FOUND)

# add more images/ Attachments later 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_media_files(request):
    try:

        with transaction.atomic():    
            task = TaskCard.objects.get(task_id=request.data.get("task_id"))

            if not task:
               return Response({"Task ID is Required"}, status=status.HTTP_400_BAD_REQUEST)

            for img in request.FILES.getlist("images"):
                TaskImage.objects.create(task_card=task, task_image=img)

            for file in request.FILES.getlist("attachments"):
                TaskAttachment.objects.create(task_card =task, task_attachment=file)

            return Response({"message": "Media Files added"}, status= status.HTTP_200_OK)
        
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status= status.HTTP_404_NOT_FOUND)

# Delete Task Media
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task_mediafile(request):
   
    try:  # recive file id and type of file from user
        mediafile_type = request.data.get("type") 
        mediafile_id = request.data.get("file_id")

        if mediafile_type == "image":
            file_obj = TaskImage.objects.get(task_image_id=mediafile_id)

        elif mediafile_type == "attachment":
            file_obj = TaskAttachment.objects.get(task_attachment_id=mediafile_id)

        else:
            return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)
        
        # validations for user can not delete others tasks files
        if file_obj.task_card.created_by != request.user:
            return Response({"error": "Can't Eddit others Media file"},status=status.HTTP_403_FORBIDDEN )

        file_obj.delete()
        return Response({"message": f"{mediafile_type} deleted"}, status= status.HTTP_200_OK)

    except (TaskImage.DoesNotExist, TaskAttachment.DoesNotExist):
        return Response({"error": "Media File not found"}, status= status.HTTP_404_NOT_FOUND)

# Update Image/Attachment 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def replace_task_mediafiles(request):

    task_id = request.data.get('task_id')
    if not task_id:
        return Response({"Please Enter Task ID"}, status= status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():    
            task = TaskCard.objects.get(task_id=task_id)

            if request.user not in task.board.members.all():
                return Response({"error": "Can't Editd others Media files"}, status=status.HTTP_403_FORBIDDEN)

            # Delete Previous img
            del_img = TaskImage.objects.filter(task=task)
            del_img.delete()

           # Delete Previous Attachment
            del_attachment = TaskAttachment.objects.filter(task=task)
            del_attachment.delete()
            
            #Replace new file
            for img in request.FILES.getlist("images"):
                TaskImage.objects.create(task=task, image=img)

            for file in request.FILES.getlist("attachments"):
                TaskAttachment.objects.create(task=task, file=file)

            return Response({"message": "All Media files replaced"}, status= status.HTTP_200_OK)
        
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status= status.HTTP_404_NOT_FOUND)    
