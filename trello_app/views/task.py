from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import *
from trello_app.serializers import *
from .authentication import activity
import json # export data in JSON file
from django.conf import settings
import csv, io, pandas as datetime  
from reportlab.lib.pagesizes import A4  # Page size for PDF export
from reportlab.lib import colors  # Colors for PDF styling
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle  # PDF generation utilities
import pandas as pd  # Pandas for Excel export
import os # File path handling

# Search Task Cards by.. various criteria including ID, title, board, description, creator, completion status, and starred status
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_tasks_by(request):
    try:
        # Base queryset: get all task cards where user is a board member, ordered by starred status
        queryset = TaskCard.objects.filter(board__members=request.user).order_by('-is_starred')
        
        task_id = request.data.get('task_id')
        title = request.data.get('title')
        board = request.data.get('board','')
        description = request.data.get('description','')
        created_by= request.data.get('created_by','')
        is_completed= request.data.get('is_completed','')
        is_starred = request.data.get('is_starred','')

        if task_id:
                queryset = queryset.filter(task_id=task_id)

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
                return Response({"status":"fail", "message": "No matching Tasks found"}, status=status.HTTP_404_NOT_FOUND)
        
        activity(request.user, f"{request.user.full_name} Searched Tasks")
        serializer = TaskCardSerializer(queryset, many=True, context={'request': request})

        return Response({"status":"success", "message":"TaskCard fetched","Task card": serializer.data}, status=status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"fail", "message":"TaskCard not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Sort task lists by newest, oldest, alphabetically, or by due date
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sort_task_lists(request):
    task_id = request.data.get("task_id")
    sort_by = request.data.get("sort_list_by")
    
    if not task_id:
        return Response({"status":"fail", "message": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        queryset = TaskList.objects.filter(task_card_id=task_id)
    except TaskCard.DoesNotExist:
        return Response({"status": "fail", "message": "TaskCard not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        if sort_by == "newest_first":
            queryset = queryset.order_by('-created_at')
        elif sort_by == "oldest_first":
            queryset = queryset.order_by('created_at')
        elif sort_by == "alphabetically":
            queryset = queryset.order_by('tasklist_title')
        elif sort_by == "due_date":
            queryset = queryset.order_by('due_date')
        else:
            return Response({"status": "fail", "error": "invalid choice"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskListSerializer(queryset, many=True, context={'request': request})
        return Response({"status": "success","message":"TaskCard sorted" ,"Task lists": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Create Task Card
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    user = request.user
    data = request.data
    required_fields = ['title', 'description', 'board_id']

    if not all(field in data and data.get(field) for field in required_fields):
        return Response({"status":"fail", "message": "Please fill all required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        try: # Get the board where the task will be created
            board = Board.objects.get(board_id=data.get("board_id"))
        except Board.DoesNotExist:
            return Response({"status":"fail", "message": "Board does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is a member of the board
        if user not in board.members.all():
            return Response({"status":"fail", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        # Define valid task status options
        valid_status = ["pending", "doing", "Completed"]
        is_completed = data.get("is_completed", "pending")

        if is_completed not in valid_status:
            return Response({"status":"fail", "message": "Invalid task status."},status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            task = TaskCard.objects.create(
                board=board,
                title=data.get("title"), 
                description=data.get("description"),
                is_completed=is_completed,
                created_by=request.user,
                updated_by=request.user,
            )

            activity(request.user, f"{request.user.full_name} created task: {task.title} in board: {board.title}")

            return Response({"status":"success", "message": "Task created successfully", "task_id": task.task_id}, status= status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Update Task Card
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request):

    data = request.data
    task_id = data.get("task_id")
    if not task_id:
        return Response({"status":"fail", "message": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task_c = TaskCard.objects.get(task_id=task_id)
    except TaskCard.DoesNotExist:
        return Response({"status":"fail", "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    # Check if user is the creator of the task (authorization)
    if request.user != task_c.created_by:
        return Response({"status":"fail", "message": "You cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)

    try:
        with transaction.atomic():  

            if 'title' in data:
                task_c.title = data['title']
            
            if 'description' in data:
                task_c.description = data['description']

            if "is_completed" in data:
                task_c.is_completed = data["is_completed"]

            task_c.save()
            activity(request.user, f"Full_Name: {request.user.full_name}, updated task: {task_c.title} in board: {task_c.board.title}")
            
            serializer = TaskCardSerializer(task_c)
            return Response({"status":"success","message": "TaskCard Updated","Updated TaskCard Detail":serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Task Card Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request):

    get_task_id = request.data.get("task_id")
    if not get_task_id:
        return Response({"status":"fail", "message": "Task ID is Required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = TaskCard.objects.get(task_id=get_task_id)
        # Check if user is the creator of the task (authorization)
        if request.user != task.created_by:
            return Response({"status":"fail", "message": "You cannot delete this task"}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        activity(request.user, f"{request.user.full_name} deleted task: {task.title} in board: {task.board.title}")
        return Response({"status":"success", "message": "Task deleted successfully"}, status= status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"fail", "message": "Task not found"}, status= status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)

# Toggle the TaskCard status as Stared or Unstarred
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_task_card(request):
    task_id = request.data.get('task_id')
    if not task_id:
        return Response({"status":"fail", "message":"please enter task_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get the task to star/unstar
        task = TaskCard.objects.get(task_id=task_id)
        # Toggle the starred status
        task.is_starred = not task.is_starred
        task.save()

        activity(request.user, f"{request.user.full_name} starred task: {task.title} in board: {task.board.title}")

        return Response({"status":"success", "message": "Task star status updated", "is_starred": task.is_starred})

    except TaskCard.DoesNotExist:
        return Response({"status":"fail", "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)

# Move task card to another board  OK
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_task_card_to_other_board(request):

    enter_task_id = request.data.get("task_id")
    new_board_id = request.data.get("new_board_id")

    if not enter_task_id and not new_board_id in request.data:
        return Response({"status":"fail", "message":"please enter task_id and new_board_id"},status = status.HTTP_400_BAD_REQUEST)

    try:
        # Get the task to move (must be created by the user)
        get_task = TaskCard.objects.get(task_id=enter_task_id, created_by=request.user)
        # Get the new board (must be created by the user)
        enter_new_board = Board.objects.get(board_id=new_board_id, created_by=request.user)

        # Update the task's board reference
        get_task.board = enter_new_board
        get_task.save()

        serializers = TaskCardSerializer(get_task)
        activity(request.user, f"{request.user.full_name} moved task: {get_task.title} to board: {enter_new_board.title}")
        return Response({"status":"success", "message": "Task moved successfully", "Task Data": serializers.data}, status=status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"fail", "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    except Board.DoesNotExist:
        return Response({"status":"fail" ,"message": "board not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Copy a Task Card along with its task lists, images, attachments, and comments
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_task_card(request):

    try:
        # Get the original TaskCard ID from request
        original_task_card_id = request.data.get("task_id")
        if not original_task_card_id:
            return Response({"status":"fail", "message": "Task ID is Required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the original task card (must be created by the user)
        get_task_card = TaskCard.objects.get(task_id=original_task_card_id, created_by=request.user)

        # this will create a copy of the task card
        with transaction.atomic():
            copy_task_card = TaskCard.objects.create(
                board=get_task_card.board,
                title=get_task_card.title,
                description=get_task_card.description,
                is_completed=get_task_card.is_completed,
                is_starred=get_task_card.is_starred,
                created_by=request.user,
                updated_by=get_task_card.updated_by,
            
            )
            # Copy all task lists from the original task card
            for tasklist in get_task_card.task_lists.all():
                with transaction.atomic():
                    # Create a copy of each task list
                    new_tasklist =TaskList.objects.create(
                        task_card=copy_task_card,
                        tasklist_title=tasklist.tasklist_title,
                        tasklist_description=tasklist.tasklist_description,
                        priority=tasklist.priority,
                        label_color=tasklist.label_color,
                        start_date=tasklist.start_date,
                        due_date=tasklist.due_date,
                        is_completed=tasklist.is_completed,
                        assigned_to=tasklist.assigned_to,
                        created_by=request.user,
                        updated_by=tasklist.updated_by,
                )
            # this will copy all images from the original task list
            for image in new_tasklist.image.all():
                TaskImage.objects.create(
                    tasks_lists_id=new_tasklist,
                    task_image=image.task_image
                )
            # this will copy all attachments from the original task list
            for attachment in new_tasklist.attachment.all():
                TaskAttachment.objects.create(
                    tasks_lists_id=new_tasklist,
                    task_attachment=attachment.task_attachment
                )
            # this will copy all comments from the original task list
            for comment in new_tasklist.comments.all():
                Comment.objects.create(
                    task_list=new_tasklist,
                    comment_text=comment.comment_text,
                    created_by=comment.created_by,
                    user=request.user,
                )
            
        activity(request.user, f"{request.user.full_name} copied task card: {get_task_card.title}")
        serializer = TaskCardSerializer(copy_task_card, context={'request': request})

        return Response({"status": "successfull", "message": "Task Card copied", "Task Card Data": serializer.data},
                        status=status.HTTP_201_CREATED)
    
    except TaskCard.DoesNotExist:
        return Response({"status": "fail", "message": "Task Card not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#########################################################
#          TASK LISTS        
#########################################################

# Function  for create Taskslists
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_lists(request):

    get_task_id = request.data.get("task_id")
    if not get_task_id:
        return Response({"status":"fail","message":"Please Enter task_id"}, status = status.HTTP_400_BAD_REQUEST)

    try:
        # Get the task card where the task list will be created
        task = TaskCard.objects.get(task_id=get_task_id)
    except TaskCard.DoesNotExist:
        return Response({"status":"fail", "message": "Entered TaskCard Not exist"}, status=status.HTTP_400_BAD_REQUEST)

     # Get assigned user ID if provided
    assigned_to_id = request.data.get("assigned_to")
    assigned_to_user = None
    if assigned_to_id:  # If assigned user ID is provided, get the user object
        try:
            assigned_to_user = User.objects.get(user_id=assigned_to_id)
        except User.DoesNotExist:
            return Response({"status":"fail", "message": "Assigned user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Create the new task list
            task_list = TaskList.objects.create(
                task_card = task,
                tasklist_title = request.data.get("tasklist_title"),
                tasklist_description = request.data.get("tasklist_description"),
                priority = request.data.get("priority"),
                label_color = request.data.get("label_color"),
                start_date = request.data.get("start_date"),
                due_date = request.data.get("due_date"),
                is_completed = request.data.get("is_completed", False),
                assigned_to = assigned_to_user,
                created_by = request.user
            )

            # save any uploaded image
            for img in request.FILES.getlist("images"):
                TaskImage.objects.create(tasks_lists_id=task_list, task_image=img)

            # save any uploaded attachments
            for file in request.FILES.getlist("attachments"):
                TaskAttachment.objects.create(tasks_lists_id=task_list, task_attachment=file)

            activity(request.user, f"{request.user.full_name} created task list: {task_list.tasklist_title} in task: {task.title}")
            serializers = TaskListSerializer(task_list, context={'request': request})
            return Response({"status":"success", "message": "Task list created", "Task List Data": serializers.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Function for Update Tasks lists
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tasks_lists(request):

    task_list_id = request.data.get("task_list_id")
    if not task_list_id:
        return Response({"status":"fail", "message":"Please Enter task_list_id"}, status= status.HTTP_400_BAD_REQUEST)

    try:    # Get the task list to update (must be created by the user)
       task_list = TaskList.objects.get(tasklist_id=task_list_id, created_by=request.user)
    except TaskList.DoesNotExist:
        return Response({"status":"fail", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if user is the creator of the task list (authorization)
    if request.user != task_list.created_by:
        return Response({"status":"fail", "message": "You cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)
    
    try:    # Get the first image and attachment associated with the task list
        task_image = TaskImage.objects.filter(tasks_lists_id=task_list).first()
        task_attachment = TaskAttachment.objects.filter(tasks_lists_id=task_list).first()

    except (TaskImage.DoesNotExist, TaskAttachment.DoesNotExist):
        return Response({"status":"fail", "message": "Task image or attachment not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        
        with transaction.atomic(): 
            # Update task list fields with new values or keep existing ones   
            task_list.tasklist_title = request.data.get("tasklist_title", task_list.tasklist_title)
            task_list.tasklist_description = request.data.get("tasklist_description", task_list.tasklist_description)
            task_list.priority = request.data.get("priority", task_list.priority)
            task_list.label_color = request.data.get("label_color", task_list.label_color)
            task_list.start_date = request.data.get("start_date", task_list.start_date)
            task_list.due_date = request.data.get("due_date", task_list.due_date)
            task_list.is_completed = request.data.get("is_completed", task_list.is_completed)
            task_list.assigned_to = request.data.get("assigned_to", task_list.assigned_to)
            
            # Process image upload if provided
            if "image" in request.FILES:
                if task_image:  # Update existing image
                    task_image.task_image = request.FILES["image"]
                    task_image.save()
                    activity(request.user, f"Full_Name: {request.user.full_name}, updated task image>>{task_image.task_image.name} in task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")
                else:   # Create new image
                    TaskImage.objects.create(tasks_lists_id=task_list, task_image=request.FILES["image"])
                    activity(request.user, f"Full_Name: {request.user.full_name}, Uploaded image>>{request.FILES['image'].name} for task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")

            # Process attachment upload if provided
            if "attachment" in request.FILES:
                if task_attachment:  # Update existing attachment
                    task_attachment.task_attachment = request.FILES["attachment"]
                    task_attachment.save()
                    activity(request.user, f"Full_Name: {request.user.full_name}, updated task attachment>>{task_attachment.task_attachment.name} for task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")
                else:   # Create new attachment
                    TaskAttachment.objects.create(tasks_lists_id=task_list, task_attachment=request.FILES["attachment"])
                    activity(request.user, f"Full_Name: {request.user.full_name}, Attached Files>>{request.FILES['attachment'].name} for task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")

        # Save the updated task list
        task_list.save()
        activity(request.user, f"{request.user.full_name} updated task list: {task_list.tasklist_title} in task: {task_list.task_card.title}")

        serializers = TaskListSerializer(task_list, context={'request': request})
        return Response({"status":"success", "message": "Task list updated", "Task List Data": serializers.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#Tasks lists Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def tasks_lists_delete(request):

    get_task_list_id = request.data.get("task_list_id")
    if not get_task_list_id:
        return Response({"status":"fail", "message":"Please Enter task_list_id"}, status= status.HTTP_400_BAD_REQUEST)

    try:    # Get the task list to delete (must be created by the user)
        task_list = TaskList.objects.get(tasklist_id=get_task_list_id, created_by=request.user)

        if request.user != task_list.created_by:  # Check if user is the creator of the task list (authorization)  
            return Response({"status":"fail", "message": "You cannot delete this task"}, status=status.HTTP_403_FORBIDDEN)

        task_list.delete()  # Delete the task list

        activity(request.user, f"{request.user.full_name} deleted task list: {task_list.tasklist_title} in task: {task_list.task_card.title}")

        return Response({"status":"successfull", "message": "Task list deleted"}, status=status.HTTP_204_NO_CONTENT)

    except TaskList.DoesNotExist:
        return Response({"status":"fail", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Copy a Task List along with its images, attachments, and comments
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_task_list(request):
    try:
        # Get the original task list ID from request
        original_task_list_id = request.data.get("task_list_id")
        if not original_task_list_id:
            return Response({"status":"fail", "message":"Please Enter task_list_id"}, status= status.HTTP_400_BAD_REQUEST)

        # Get the original task list (must be created by the user)
        get_task_list = TaskList.objects.get(tasklist_id=original_task_list_id, created_by=request.user)
        
        with transaction.atomic():
            # Create a copy of the task list
            copy_task_list = TaskList.objects.create(
                        task_card=get_task_list.task_card,                              
                        tasklist_title  =  get_task_list.tasklist_title,
                        tasklist_description  =  get_task_list.tasklist_description,
                        priority  =  get_task_list.priority,
                        label_color  =  get_task_list.label_color,
                        start_date  =  get_task_list.start_date,
                        due_date  =  get_task_list.due_date,
                        is_completed  =  get_task_list.is_completed,
                        assigned_to  =  get_task_list.assigned_to,
                        created_by  =  request.user
                    ) 
            # this will copy all images from the original task list
            for image in get_task_list.image.all():
                TaskImage.objects.create(
                    tasks_lists_id=copy_task_list,
                    task_image=image.task_image,
                    uploaded_by=request.user
                )
            # this will copy all attachments from the original task list
            for attachment in get_task_list.attachment.all():
                TaskAttachment.objects.create(
                    tasks_lists_id=copy_task_list,
                    task_attachment=attachment.task_attachment,
                    uploaded_by=request.user
                )
            # this will copy all comments from the original task list
            for comment in get_task_list.comments.all():
                Comment.objects.create(
                    task_list=copy_task_list,
                    comment_text=comment.comment_text,
                    created_by=request.user,
                    user=request.user
                )

        activity(request.user, f"{request.user.full_name} copied task list: {get_task_list.tasklist_title}")

        serializers = TaskListSerializer(copy_task_list)
        return Response({"status": "successfull", "message": "Task list copied", "Task List Data": serializers.data},
                          status=status.HTTP_201_CREATED)

    except TaskList.DoesNotExist:
        return Response({"status":"fail", "message": "Original task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Move tasks list to other tasks card 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_task_list(request):
    try:
        # Get task list ID and new task card ID from request
        enter_tasklist_id = request.data.get("task_list_id")
        new_task_card_id = request.data.get("new_task_card_id")
        
        if not enter_tasklist_id or new_task_card_id:
            return Response({"status":"success", "message":"Please enter task_list_id, new_task_card_id "}, status=status.HTTP_400_BAD_REQUEST)

        # Get the task list to move (must be created by the user)
        task_list = TaskList.objects.get(tasklist_id = enter_tasklist_id, created_by = request.user)

        # Get the new task card (must be created by the user)
        new_task_card = TaskCard.objects.get(task_id = new_task_card_id, created_by = request.user)
        
        # Update the task list's task card reference
        task_list.task_card = new_task_card
        task_list.save()

        activity(request.user, f"{request.user.full_name} moved task list: {task_list.tasklist_title} to task card: {new_task_card.title}")
        
        serializers = TaskListSerializer(task_list)
        return Response({"status": "successfull", "message": "Task list moved", "Task List Data": serializers.data}, status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"status":"fail", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except TaskCard.DoesNotExist:
        return Response({"status":"fail", "message": "New task card not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Manage checklist items for a task list with title
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tasklist_checklist_progress(request):
    try:    # Get task list ID and checklist items from request
        task_list_id = request.data.get("task_list_id")
        get_checklist_items = request.data.get("checklist_items", {})

        if not task_list_id:
            return Response({"status": "fail", "message": "task_list_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the task list to update (must be created by the user)
        task_list = TaskList.objects.get(tasklist_id=task_list_id, created_by=request.user)

        # Merging old and new checklist items
        old_checklist = task_list.checklist_items or {"title": "", "items": []}  # Ensure old checklist is initialized
        title = get_checklist_items.get("title", old_checklist.get("title", ""))

        # If title is not provided in both old and new, set a default title
        if not title:
            title = "Checklist"

        # Merging items based on name to avoid duplicates
        old_items = old_checklist.get("items", [])
        new_items = get_checklist_items.get("items", [])

        # Using a dictionary to merge old and new items by name
        merged = {item["name"]: item for item in old_items + new_items}

        # Preserving the order of items based on their first occurrence
        result = {"title": title,"items": [merged[key] for key in merged]}

        # Update the task list's checklist items
        task_list.checklist_items = result
        task_list.save()

        activity(request.user, f"{request.user.full_name} updated task list progress: {task_list.tasklist_title}")

        serializers = TaskListSerializer(task_list)
        return Response({"status": "successfull", "message": "Task list progress updated", "Data": serializers.data}, 
                        status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"status": "fail", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Update the checked status of a checklist item
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_checkbox(request):
    # Get TaskList ID, item name, and checked status from request
    get_tasklist_id = request.data.get("tasklist_id")
    get_item_name = request.data.get("name")
    get_is_checked = request.data.get("is_checked", False)

    if not get_tasklist_id or not get_item_name:
        return Response({"status": "fail", "message": "tasklist_id and item name are required"},status=status.HTTP_400_BAD_REQUEST)

    try:   
        # Get the task list to update (must be created by the user)
        task_list = TaskList.objects.get(tasklist_id=get_tasklist_id, created_by=request.user)

        # Get the current checklist items
        checklist = task_list.checklist_items or {}

        # If checklist is stored as string, parse it to JSON
        if isinstance(checklist, str):
            checklist = json.loads(checklist)
        
        # Get the items from the checklist
        items = checklist.get("items", [])

        # Find and update the specified item
        updated = False
        for item in items:
            if item.get("name") == get_item_name:
                item["done"] = True if str(get_is_checked).lower() == "true" else False
                updated = True
                break

        if not updated:
            return Response({"status": "fail", "message": f"checklist item '{get_item_name}' not found"},status=status.HTTP_404_NOT_FOUND)

        # Update the checklist items
        checklist["items"] = items
        task_list.checklist_items = checklist
        task_list.save()

        activity(request.user, f"{request.user.full_name} updated checklist item '{get_item_name}' in {task_list.tasklist_title}")

        return Response({"status": "success", "message": f"checklist item '{get_item_name}' updated successfully"}, status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"status": "fail", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# delete checklist item
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_checklist(request):
    # Get task list ID and optional item name from request
    get_tasklist_id = request.data.get("tasklist_id")
    get_item_name = request.data.get("name")

    try:
        # Get the task list to update (must be created by the user)
        task_list = TaskList.objects.get(tasklist_id=get_tasklist_id, created_by=request.user)

        # Get the current checklist items
        checklist = task_list.checklist_items or {}

        # If checklist is stored as string, parse it to JSON
        if isinstance(checklist, str):
            checklist = json.loads(checklist)

        # Get the items from the checklist
        items = checklist.get("items", [])

        # Check if specific item or CheckBox provided and delete them.
        if get_item_name: # filter out that specified item
            new_items = [item for item in items if item.get("name") != get_item_name]

            if len(new_items) == len(items):
                return Response({"status": "fail", "message": f"item '{get_item_name}' not found in checklist"},status=status.HTTP_404_NOT_FOUND)

            # Update the checklist items
            checklist["items"] = new_items
            task_list.checklist_items = checklist
            msg = f"checklist item '{get_item_name}' deleted successfully"

            activity(request.user, f"{request.user.full_name} deleted checklist item '{get_item_name}' from {task_list.tasklist_title}")

        # If no item provided then delete entire CheckBox
        else:
            task_list.checklist_items = {"title": checklist.get("title", ""), "items": []}
            msg = "All checklist items deleted"

            activity(request.user, f"{request.user.full_name} cleared all checklist items in {task_list.tasklist_title}")

        task_list.save()
        return Response({"status": "success", "message": msg}, status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"status": "fail", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# features for convert checkbox into tasklist
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convert_checkbox_to_tasklist(request):
    get_tasklist_id = request.data.get("tasklist_id")
    get_item_name = request.data.get("name")

    if not get_tasklist_id or not get_item_name:
        return Response({"status": "fail", "message": "tasklist_id and item name are required"},status=status.HTTP_400_BAD_REQUEST,)

    try:
        # Get the task list containing the checklist (must be created by the user)
        task_list = TaskList.objects.get(tasklist_id=get_tasklist_id, created_by=request.user)

        # Get the checklist items
        checklist = task_list.checklist_items or {} # If task_list.checklist_items is None or empty (falsy), it will assigns an empty dictionary {} instead.
        checklist_items = checklist.get("items", []) # If "items" doesn’t exist, it defaults to an empty list [].

        # Find the specified checklist item
        for item in checklist_items:
            if item.get("name") == get_item_name:
                # Create a new task list from the checklist item
                new_task = TaskList.objects.create(
                    tasklist_title=item.get("name"),
                    tasklist_description=item.get("description", ""),
                    task_card=task_list.task_card,
                    created_by=request.user)

                activity(request.user,f"{request.user.full_name} converted checklist item: {get_item_name} to task {new_task.tasklist_title}")

                return Response({"status": "success","message": f"Checklist item '{get_item_name}' converted to task '{new_task.tasklist_title}'"},
                                  status=status.HTTP_200_OK)

        return Response({"status": "fail", "message": f"Checklist item '{get_item_name}' not found"}, status=status.HTTP_404_NOT_FOUND,)

    except TaskList.DoesNotExist:
        return Response({"status": "fail", "message": "Task list not found"},status=status.HTTP_404_NOT_FOUND,)

    except Exception as e:
        return Response({"status": "error", "message": str(e)},status=status.HTTP_400_BAD_REQUEST,)

# Function for comments in TaskLists
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request):
    user = request.user
    data = request.data

    if not data.get('tasklist_id') or not data.get('comment_text'):
        return Response({"status":"error", "message": "Task list and comment text required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task_list = TaskList.objects.get(tasklist_id=data['tasklist_id'])
        comment = Comment.objects.create(
            user=user,
            task_list=task_list,
            comment_text=data['comment_text'],
            created_by=request.user,
            updated_by=request.user
        )

        activity(user, f"{user.full_name} commented on task list: {task_list.tasklist_title}")
        serializer = CommentDetailSerializer(comment)
        return Response({"status": "success", "message": "Comment created successfully", "Comment data": serializer.data}, 
                        status=status.HTTP_201_CREATED)

    except TaskList.DoesNotExist:
        return Response({"status": "fail", "message": "task list does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Function for Edit Comments in TaskLists
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_comment(request):

    comment_id = request.data.get('comment_id')
    comment_text = request.data.get('comment_text')

    if not comment_id or not comment_text:
        return Response({"status":"fail", "message": "comment_id and comment_text required"}, status=status.HTTP_400_BAD_REQUEST)

    try:    # User can edit only their own comment
        comment = Comment.objects.get(comment_id=request.data['comment_id'], user=request.user)
        comment.comment_text = request.data['comment_text']
        comment.save()

        activity(request.user, f"{request.user.full_name} edited a comment on task list: {comment.task_list.tasklist_title}")
        serializer = CommentDetailSerializer(comment)
        return Response({"status": "success", "message": "Comment updated successfully", "Updated Comment Data": serializer.data},
                        status=status.HTTP_200_OK)

    except Comment.DoesNotExist:
        return Response({"status": "fail", "message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Function for Delete Comments in TaskLists
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request):

    if not request.data.get('comment_id'):
        return Response({"status":"fail", "message": "Comment ID required"}, status=status.HTTP_400_BAD_REQUEST)

    try:    # User can delete only their own comment
        comment = Comment.objects.get(comment_id=request.data['comment_id'], user=request.user)
        comment.delete()
        activity(request.user, f"{request.user.full_name} deleted a comment from task list: {comment.task_list.tasklist_title}")

        return Response({"status": "success", "message": "Comment deleted successfully"},
                        status=status.HTTP_200_OK)

    except Comment.DoesNotExist:
        return Response({"status": "fail", "message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Print, Export as PDF, Json, CSV functionality (TaskList based)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def print_export(request):
    user = request.user
    tasklist_id = request.data.get("tasklist_id")
    export_format = request.data.get("format", "").lower()
    
    if not tasklist_id:
        return Response({"status": "fail", "message": "tasklist_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get the TaskCard (just for board relation + filter)
        task_card = TaskCard.objects.get(task_id=tasklist_id, created_by=user)

        # Permission check
        if user not in task_card.board.members.all():
            return Response({"status": "fail", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        # Get all TaskLists under this TaskCard
        tasklists = TaskList.objects.filter(task_card=task_card)

        if not tasklists.exists():
            return Response({"status": "fail", "message": "No TaskLists found for this TaskCard"}, status=status.HTTP_404_NOT_FOUND)

        # ---------------- JSON Export ----------------
        if export_format == "json":
            data = []
            for tl in tasklists:
                data.append({
                    # "TaskCard": tl.task_card,
                    "TaskList ID": tl.tasklist_id,
                    "Title": tl.tasklist_title,
                    "Description": tl.tasklist_description,
                    "Priority": tl.priority,
                    "Label Color": tl.label_color,
                    "Start Date": str(tl.start_date) if tl.start_date else None,
                    "Due Date": str(tl.due_date) if tl.due_date else None,
                    "Assigned User": tl.assigned_to.username if tl.assigned_to else "Unassigned",
                    "Status": "Completed" if tl.is_completed else "Pending",
                    "CheckBox": tl.checklist_items,
                })

            file_name = f"tasklists_{tasklist_id}.json"
            file_path = os.path.join(settings.MEDIA_ROOT, "exports", file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            return Response({"status": "success", "message": f"JSON file saved at {file_path}"}, status=status.HTTP_200_OK)

        # ---------------- CSV Export ----------------
        elif export_format == "csv":
            file_name = f"tasklists_{tasklist_id}.csv"
            file_path = os.path.join(settings.MEDIA_ROOT, "exports", file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["TaskList ID", "Task Card","TaskList Title", "TaskList Description", "Priority", "Label Color", "Start Date", "Due Date", "CheckList Items","Assigned User", "Status"])

                for tl in tasklists:
                    writer.writerow([
                        tl.tasklist_id,
                        tl.task_card,
                        tl.tasklist_title,
                        tl.tasklist_description,
                        tl.priority,
                        tl.label_color,
                        tl.start_date,
                        tl.due_date,
                        tl.checklist_items,
                        tl.assigned_to.username if tl.assigned_to else "Unassigned",
                        "Completed" if tl.is_completed else "Pending"
                    ])

            return Response({"status": "success", "message": f"CSV file saved at {file_path}"}, status=status.HTTP_200_OK)

        # ---------------- PDF Export ----------------
        elif export_format == "pdf":
            file_name = f"tasklists_{tasklist_id}.pdf"
            file_path = os.path.join(settings.MEDIA_ROOT, "exports", file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            data = [["TaskCard","TaskList Title", "Priority", "Due Date", "Assigned User", "Status"]]
            for tl in tasklists:
                data.append([
                    tl.task_card,
                    tl.tasklist_title,
                    tl.priority,
                    str(tl.due_date) if tl.due_date else "",
                    tl.assigned_to.username if tl.assigned_to else "Unassigned",
                    "Completed" if tl.is_completed else "Pending",
                ])

            pdf = SimpleDocTemplate(file_path, pagesize=A4)
            table = Table(data, colWidths=[110, 130, 70, 80, 100, 70])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            pdf.build([table])

            return Response({"status": "success", "message": f"PDF file saved at {file_path}"}, status=status.HTTP_200_OK)

        # ---------------- Excel Export ----------------
        elif export_format == "excel":
            file_name = f"tasklists_{tasklist_id}.xlsx"
            file_path = os.path.join(settings.MEDIA_ROOT, "exports", file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            rows = []
            for tl in tasklists:
                rows.append({
                    "TaskCard": tl.task_card,
                    "TaskList ID": tl.tasklist_id,
                    "Title": tl.tasklist_title,
                    "Description": tl.tasklist_description,
                    "Priority": tl.priority,
                    "Label Color": tl.label_color,
                    "Start Date": tl.start_date,
                    "Due Date": tl.due_date,
                    "Assigned User": tl.assigned_to.username if tl.assigned_to else "Unassigned",
                    "Status": "Completed" if tl.is_completed else "Pending",
                    "CheckBox": tl.checklist_items,
                })

            df = pd.DataFrame(rows)
            df.to_excel(file_path, index=False, engine="openpyxl")

            return Response({"status": "success", "message": f"Excel file saved at {file_path}"}, status=status.HTTP_200_OK)

        else:
            return Response({"status": "fail", "message": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)

    except TaskCard.DoesNotExist:
        return Response({"status": "fail", "message": "TaskCard not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)