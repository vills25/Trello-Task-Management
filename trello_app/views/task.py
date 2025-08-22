from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import *
from trello_app.serializers import *
from .authentication import activity

# Search Task Cards    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_tasks(request):
    try:
        data = request.data
        queryset = TaskCard.objects.filter(board__members=request.user).order_by('-is_starred')
        
        task_id = data.get('task_id')
        title = data.get('title')
        board = data.get('board','')
        description = data.get('description','')
        created_by= data.get('created_by','')
        is_completed= data.get('is_completed','')
        is_starred = data.get('is_starred','')
        
        if task_id:
                queryset = queryset.filter(pk=task_id)

        if title:
            queryset = queryset.filter(title__icontains = title)

        if board:
                queryset = queryset.filter(board__board_id__icontains=board)

        if description:
                queryset = queryset.filter(description__icontains=description)

        if created_by:
                queryset =  queryset.filter(created_by__username__icontains=created_by) | queryset.filter(created_by__full_name__icontains=created_by)

        if is_completed:
                queryset = queryset.filter(is_completed__icontains=is_completed)

        if is_starred:
                queryset = queryset.filter(is_starred__icontains=is_starred)

        if not queryset.exists():
                return Response({"message": "No matching Tasks found"}, status=status.HTTP_404_NOT_FOUND)
        
        activity(request.user, f"{request.user.full_name} Searched Tasks")
        serializer = TaskCardSerializer(queryset, many=True)
        return Response({"Task card": serializer.data}, status=status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"Task not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        
        valid_status = ["pending", "doing", "Completed"]
        is_completed = data.get("is_completed", "pending")

        if is_completed not in valid_status:
            return Response({"error": "Invalid task status."},status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            task = TaskCard.objects.create(
                board=board,
                title=data.get("title"), 
                description=data.get("description"),
                is_completed=is_completed,
                created_by=request.user,
                updated_by=request.user,
            )
                
            for img in request.FILES.getlist("images"):
                TaskImage.objects.create(task_card=task, task_image=img)

            for file in request.FILES.getlist("attachments"):
                TaskAttachment.objects.create(task_card=task, task_attachment=file)
            
            assigned_to_id = data.get("assigned_to")
            assigned_to_user = None
            if assigned_to_id:
                try:
                    assigned_to_user = User.objects.get(user_id=assigned_to_id)
                except User.DoesNotExist:
                    return Response({"error": "Assigned user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                
            activity(request.user, f"{request.user.full_name} created task: {task.title} in board: {board.title}")

            subtasks = data.get('task_lists', [])
            for sub in subtasks:
                if sub.get("tasklist_title") and sub.get("tasklist_description"):
                        TaskList.objects.create(
                            task_card=task,
                            tasklist_title=sub.get("tasklist_title"),
                            tasklist_description=sub.get("tasklist_description"),
                            priority=sub.get("priority"),
                            label_color=sub.get("label_color"),
                            start_date=sub.get("start_date"),
                            due_date=sub.get("due_date"),
                            is_completed=sub.get("is_completed", False),
                            assigned_to=assigned_to_user,
                            created_by=request.user,
                            updated_by=request.user
                        )
            activity(request.user, f"{request.user.full_name} created task:: {task.title} with subtasks in board:: {board.title}")
            return Response({"message": "Task created successfully", "task_id": task.task_id}, status= status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Update Task Card
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request):

    data = request.data
    task_id = data.get("task_id")

    if not task_id:
        return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task_c = TaskCard.objects.get(task_id=task_id)
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user != task_c.created_by:
        return Response({"error": "You cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)

    task_image = TaskImage.objects.filter(task_card=task_c).first()
    task_attachment = TaskAttachment.objects.filter(task_card=task_c).first()

    try:
        with transaction.atomic():  

            if 'title' in data:
                task_c.title = data['title']
            
            if 'description' in data:
                task_c.description = data['description']
            
            if "image" in request.FILES:
                if task_image:
                    task_image.task_image = request.FILES["image"]
                    task_image.save()
                    activity(request.user, f"Full_Name: {request.user.full_name}, updated task image>>{task_image.task_image.name} in task: {task_c.title} in board: {task_c.board.title}")
                else:
                    TaskImage.objects.create(task=task_c, image=request.FILES["image"])
                    activity(request.user, f"Full_Name: {request.user.full_name}, added task image>>{request.FILES['image'].name} for task: {task_c.title} in board: {task_c.board.title}")

            if "is_completed" in data:
                task_c.is_completed = data["is_completed"]
                
            if "attachment" in request.FILES:
                if task_attachment:
                    task_attachment.task_attachment = request.FILES["attachment"]
                    task_attachment.save()
                    activity(request.user, f"Full_Name: {request.user.full_name}, updated task attachment>>{task_attachment.task_attachment.name} for task: {task_c.title} in board: {task_c.board.title}")
                else:
                    TaskAttachment.objects.create(task=task_c, file=request.FILES["attachment"])
                    activity(request.user, f"Full_Name: {request.user.full_name}, added task attachment>>{request.FILES['attachment'].name} for task: {task_c.title} in board: {task_c.board.title}")

            task_c.save()
            activity(request.user, f"Full_Name: {request.user.full_name}, updated task: {task_c.title} in board: {task_c.board.title}")
            
            serializer = TaskCardSerializer(task_c)
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
        activity(request.user, f"{request.user.full_name} deleted task: {task.title} in board: {task.board.title}")
        return Response({"message": "Task deleted successfully"}, status= status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status= status.HTTP_404_NOT_FOUND)
 
# Give Star To Task
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_task_card(request):
    task_id = request.data.get('task_id')
    try:
        task = TaskCard.objects.get(task_id=task_id)
        task.is_starred = not task.is_starred
        task.save()
        activity(request.user, f"{request.user.full_name} starred task: {task.title} in board: {task.board.title}")
        return Response({"message": "Task star status updated", "is_starred": task.is_starred})
    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################

# Function  for create Taskslists
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_list(request):

    task_id = request.data.get("task_id")
    task = TaskCard.objects.get(id=task_id)

    if not task:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        task_list = TaskList.objects.create(
            task_card = task,
            tasklist_title = request.data.get("tasklist_title"),
            tasklist_description = request.data.get("tasklist_description"),
            priority = request.data.get("priority"),
            label_color = request.data.get("label_color"),
            start_date = request.data.get("start_date"),
            due_date = request.data.get("due_date"),
            is_completed = request.data.get("is_completed", False),
            assigned_to = request.data.get("assigned_to"),
            created_by = request.user
        )
        activity(request.user, f"{request.user.full_name} created task list: {task_list.tasklist_title} in task: {task.title}")
        return Response({"Status":"Successfull", "message": "Task list created", "Task List Data": TaskListSerializer(task_list).data}, status=status.HTTP_201_CREATED)

    except TaskCard.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# Function for Update Tasks lists
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tasks_lists(request):

    task_list_id = request.data.get("task_list_id")

    try:
        task_list = TaskList.objects.get(id=task_list_id, created_by=request.user)

        task_list.tasklist_title = request.data.get("tasklist_title", task_list.tasklist_title)
        task_list.tasklist_description = request.data.get("tasklist_description", task_list.tasklist_description)
        task_list.priority = request.data.get("priority", task_list.priority)
        task_list.label_color = request.data.get("label_color", task_list.label_color)
        task_list.start_date = request.data.get("start_date", task_list.start_date)
        task_list.due_date = request.data.get("due_date", task_list.due_date)
        task_list.is_completed = request.data.get("is_completed", task_list.is_completed)
        task_list.assigned_to = request.data.get("assigned_to", task_list.assigned_to)

        task_list.save()
        activity(request.user, f"{request.user.full_name} updated task list: {task_list.tasklist_title} in task: {task_list.task_card.title}")
        return Response({"Status":"Successfull", "message": "Task list updated", "Task List Data": TaskListSerializer(task_list).data}, status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"error": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Function For Tasks lists Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def tasks_lists_delete(request):

    task_list_id = request.data.get("task_list_id")

    try:
        task_list = TaskList.objects.get(id=task_list_id, created_by=request.user)
        task_list.delete()

        activity(request.user, f"{request.user.full_name} deleted task list: {task_list.tasklist_title} in task: {task_list.task_card.title}")

        return Response({"Status":"Successfull", "message": "Task list deleted"}, status=status.HTTP_204_NO_CONTENT)

    except TaskList.DoesNotExist:
        return Response({"error": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)