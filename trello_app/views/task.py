from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import *
from trello_app.serializers import *
from .authentication import activity

# Search Task Cards by..    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_tasks_by(request):
    try:

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
                return Response({"status":"error", "message": "No matching Tasks found"}, status=status.HTTP_404_NOT_FOUND)
        
        activity(request.user, f"{request.user.full_name} Searched Tasks")
        serializer = TaskCardSerializer(queryset, many=True)
        return Response({"status":"success", "Task card": serializer.data}, status=status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message":"TaskCard not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Sort lists of card by newest, oldest first and by Alphabet
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sort_task_lists(request):
    task_id = request.data.get("task_id")
    sort_by = request.data.get("sort_list_by")
    
    if not task_id:
        return Response({"status":"error", "message": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        queryset = TaskList.objects.filter(task_card_id=task_id)
    except TaskCard.DoesNotExist:
        return Response({"status": "error", "message": "TaskCard not found"}, status=status.HTTP_404_NOT_FOUND)

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

        serializer = TaskListSerializer(queryset, many=True)
        return Response({"status": "success", "Task lists": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status": "fail", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Create Task Card
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    user = request.user
    data = request.data
    required_fields = ['title', 'description', 'board_id']

    if not all(field in data and data.get(field) for field in required_fields):
        return Response({"status":"error", "message": "Please fill all required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        try:
            board = Board.objects.get(board_id=data.get("board_id"))
        except Board.DoesNotExist:
            return Response({"status":"error", "message": "Board does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if user not in board.members.all():
            return Response({"status":"error", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        valid_status = ["pending", "doing", "Completed"]
        is_completed = data.get("is_completed", "pending")

        if is_completed not in valid_status:
            return Response({"status":"error", "message": "Invalid task status."},status=status.HTTP_400_BAD_REQUEST)

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
        return Response({"status":"error", "message": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task_c = TaskCard.objects.get(task_id=task_id)
    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user != task_c.created_by:
        return Response({"status":"error", "message": "You cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({"status":"success, Updated","Updated task Details":serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Task Card Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request):

    task_id = request.data.get("task_id")
    if not task_id:
        return Response({"status":"error", "message": "Task ID is Required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = TaskCard.objects.get(id=task_id)
        if request.user != task.created_by:
            return Response({"status":"error", "message": "You cannot delete this task"}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        activity(request.user, f"{request.user.full_name} deleted task: {task.title} in board: {task.board.title}")
        return Response({"status":"success", "message": "Task deleted successfully"}, status= status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "Task not found"}, status= status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)

# Give Star To Task
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_task_card(request):
    task_id = request.data.get('task_id')
    if not task_id:
        return Response({"status":"error", "message":"please enter task_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = TaskCard.objects.get(task_id=task_id)
        task.is_starred = not task.is_starred
        task.save()

        activity(request.user, f"{request.user.full_name} starred task: {task.title} in board: {task.board.title}")

        return Response({"status":"success", "message": "Task star status updated", "is_starred": task.is_starred})

    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)

# Move task card to another board  OK
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_task_card_to_other_board(request):

    enter_task_id = request.data.get("task_id")
    new_board_id = request.data.get("new_board_id")

    if not enter_task_id and not new_board_id in request.data:
        return Response({"status":"error", "message":"please enter task_id and new_board_id"},status = status.HTTP_400_BAD_REQUEST)

    try:
        
        get_task = TaskCard.objects.get(task_id=enter_task_id, created_by=request.user)
        enter_new_board = Board.objects.get(board_id=new_board_id, created_by=request.user)

        get_task.board = enter_new_board
        get_task.save()
        

        serializers = TaskCardSerializer(get_task)
        activity(request.user, f"{request.user.full_name} moved task: {get_task.title} to board: {enter_new_board.title}")
        return Response({"status":"success", "message": "Task moved successfully", "Task Data": serializers.data}, status=status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    except Board.DoesNotExist:
        return Response({"status":"error" ,"message": "board not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Copy Tasks Card   OK
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_task_card(request):

    try:
        original_task_card_id = request.data.get("task_id")
        if not original_task_card_id:
            return Response({"status":"error", "message": "Task ID is Required"}, status=status.HTTP_400_BAD_REQUEST)
        
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
        # this will create a copy of the task lists
            for tasklist in get_task_card.task_lists.all():
                with transaction.atomic():
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
        serializer = TaskCardSerializer(copy_task_card)

        return Response({"status": "successfull", "message": "Task Card copied", "Task Card Data": serializer.data},
                        status=status.HTTP_201_CREATED)
    
    except TaskCard.DoesNotExist:
        return Response({"status": "error", "message": "Task Card not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

###########################################################################################################################################
#          TASK LISTS         #############################################################################################################
###########################################################################################################################################

# Function  for create Taskslists
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_lists(request):

    get_task_id = request.data.get("task_id")
    if not get_task_id:
        return Response({"status":"error","message":"Please Enter task_id"}, status = status.HTTP_400_BAD_REQUEST)

    try:
        task = TaskCard.objects.get(task_id=get_task_id)
    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "Entered TaskCard Not exist"}, status=status.HTTP_400_BAD_REQUEST)

    assigned_to_id = request.data.get("assigned_to")
    assigned_to_user = None
    if assigned_to_id:
        try:
            assigned_to_user = User.objects.get(user_id=assigned_to_id)
        except User.DoesNotExist:
            return Response({"status":"error", "message": "Assigned user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
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

            for img in request.FILES.getlist("images"):
                TaskImage.objects.create(tasks_lists_id=task_list, task_image=img)

            for file in request.FILES.getlist("attachments"):
                TaskAttachment.objects.create(tasks_lists_id=task_list, task_attachment=file)

            activity(request.user, f"{request.user.full_name} created task list: {task_list.tasklist_title} in task: {task.title}")
            serializers = TaskListSerializer(task_list)
            return Response({"atatus":"success", "message": "Task list created", "Task List Data": serializers.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Function for Update Tasks lists
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tasks_lists(request):

    task_list_id = request.data.get("task_list_id")
    if not task_list_id:
        return Response({"status":"error", "message":"Please Enter task_list_id"}, status= status.HTTP_400_BAD_REQUEST)

    try:
       task_list = TaskList.objects.get(tasklist_id=task_list_id, created_by=request.user)
    except TaskList.DoesNotExist:
        return Response({"status":"error", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user != task_list.created_by:
        return Response({"status":"error", "message": "You cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        task_image = TaskImage.objects.filter(tasks_lists_id=task_list).first()
        task_attachment = TaskAttachment.objects.filter(tasks_lists_id=task_list).first()

    except (TaskImage.DoesNotExist, TaskAttachment.DoesNotExist):
        return Response({"status":"error", "message": "Task image or attachment not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        
        with transaction.atomic():    
            task_list.tasklist_title = request.data.get("tasklist_title", task_list.tasklist_title)
            task_list.tasklist_description = request.data.get("tasklist_description", task_list.tasklist_description)
            task_list.priority = request.data.get("priority", task_list.priority)
            task_list.label_color = request.data.get("label_color", task_list.label_color)
            task_list.start_date = request.data.get("start_date", task_list.start_date)
            task_list.due_date = request.data.get("due_date", task_list.due_date)
            task_list.is_completed = request.data.get("is_completed", task_list.is_completed)
            task_list.assigned_to = request.data.get("assigned_to", task_list.assigned_to)
             
            if "image" in request.FILES:
                if task_image:
                    task_image.task_image = request.FILES["image"]
                    task_image.save()
                    activity(request.user, f"Full_Name: {request.user.full_name}, updated task image>>{task_image.task_image.name} in task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")
                else:
                    TaskImage.objects.create(tasks_lists_id=task_list, task_image=request.FILES["image"])
                    activity(request.user, f"Full_Name: {request.user.full_name}, Uploaded image>>{request.FILES['image'].name} for task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")

            if "attachment" in request.FILES:
                if task_attachment:
                    task_attachment.task_attachment = request.FILES["attachment"]
                    task_attachment.save()
                    activity(request.user, f"Full_Name: {request.user.full_name}, updated task attachment>>{task_attachment.task_attachment.name} for task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")
                else:
                    TaskAttachment.objects.create(tasks_lists_id=task_list, task_attachment=request.FILES["attachment"])
                    activity(request.user, f"Full_Name: {request.user.full_name}, Attached Files>>{request.FILES['attachment'].name} for task: {task_list.tasklist_title} in board: {task_list.task_card.board.title}")

        task_list.save()
        activity(request.user, f"{request.user.full_name} updated task list: {task_list.tasklist_title} in task: {task_list.task_card.title}")

        serializers = TaskListSerializer(task_list)
        return Response({"status":"success", "message": "Task list updated", "Task List Data": serializers.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#Tasks lists Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def tasks_lists_delete(request):

    get_task_list_id = request.data.get("task_list_id")
    if not get_task_list_id:
        return Response({"status":"error", "message":"Please Enter task_list_id"}, status= status.HTTP_400_BAD_REQUEST)

    try:
        task_list = TaskList.objects.get(tasklist_id=get_task_list_id, created_by=request.user)

        if request.user != task_list.created_by:
            return Response({"status":"error", "message": "You cannot delete this task"}, status=status.HTTP_403_FORBIDDEN)

        task_list.delete()

        activity(request.user, f"{request.user.full_name} deleted task list: {task_list.tasklist_title} in task: {task_list.task_card.title}")

        return Response({"status":"successfull", "message": "Task list deleted"}, status=status.HTTP_204_NO_CONTENT)

    except TaskList.DoesNotExist:
        return Response({"status":"error", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Copy task lists  OK
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_task_list(request):
    try:
        original_task_list_id = request.data.get("task_list_id")
        if not original_task_list_id:
            return Response({"status":"error", "message":"Please Enter task_list_id"}, status= status.HTTP_400_BAD_REQUEST)
        
        get_task_list = TaskList.objects.get(tasklist_id=original_task_list_id, created_by=request.user)
        
        with transaction.atomic():
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
        return Response({"status":"error", "message": "Original task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Move tasks list to other tasks card  OK
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_task_list(request):
    try:
        enter_tasklist_id = request.data.get("task_list_id")
        new_task_card_id = request.data.get("new_task_card_id")
        
        if not enter_tasklist_id or new_task_card_id:
            return Response({"status":"success", "message":"Please enter task_list_id, new_task_card_id "}, status=status.HTTP_400_BAD_REQUEST)

        task_list = TaskList.objects.get(tasklist_id = enter_tasklist_id, created_by = request.user)
        new_task_card = TaskCard.objects.get(task_id = new_task_card_id, created_by = request.user)
        
        task_list.task_card = new_task_card
        task_list.save()

        activity(request.user, f"{request.user.full_name} moved task list: {task_list.tasklist_title} to task card: {new_task_card.title}")
        
        serializers = TaskListSerializer(task_list)
        return Response({"status": "successfull", "message": "Task list moved", "Task List Data": serializers.data}, status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"status":"error", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "New task card not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# checklist box 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_list_checklist_progress(request):
    try:
        task_list_id = request.data.get("task_list_id")
        get_checklist_items = request.data.get("checklist_items", [])

        if not task_list_id:
            return Response({"status": "error", "message": "Task list ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        task_list = TaskList.objects.get(tasklist_id=task_list_id, created_by=request.user)
        task_list.checklist_items = get_checklist_items
        task_list.save()

        activity(request.user, f"{request.user.full_name} updated task list progress: {task_list.tasklist_title}")

        serializers = TaskListSerializer(task_list)
        return Response({"status": "successfull", "message": "Task list progress updated", "Task List Data": serializers.data}, status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"status": "error", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
