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

            activity(request.user, f"{request.user.full_name} created task: {task.title} in board: {board.title}")
    
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

        activity(request.user, f"{request.user.full_name} moved task: {get_task.title} to board: {enter_new_board.title}")
        return Response({"status":"success", "message": "Task moved successfully", "Task Data": TaskCardSerializer(get_task).data}, status=status.HTTP_200_OK)

    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    except Board.DoesNotExist:
        return Response({"status":"error" ,"message": "board not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Copy Tasks Card   OK
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_task_card(request):

    try:
        original_task_card_id = request.data.get("task_id")
        get_task_card = TaskCard.objects.get(task_id=original_task_card_id, created_by=request.user)
        
        copy_task_card = TaskCard.objects.create(
            board=get_task_card.board,
            title=get_task_card.title,
            description=get_task_card.description,
            is_completed=get_task_card.is_completed,
            is_starred=get_task_card.is_starred,
            created_by=request.user,
            updated_by=get_task_card.updated_by,
      
        )

        for tasklist in get_task_card.task_lists.all():
            TaskList.objects.create(
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
        

        activity(request.user, f"{request.user.full_name} copied task card: {get_task_card.title}")
        serializer = TaskCardSerializer(copy_task_card)

        return Response({"status": "successfull", "message": "Task Card copied", "Task Card Data": serializer.data},
                        status=status.HTTP_201_CREATED)
    
    except TaskCard.DoesNotExist:
        return Response({"status": "error", "message": "Task Card not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

###########################################################################################################################################
#          TASK LISTS         #############################################################################################################
###########################################################################################################################################

# Function  for create Taskslists
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_lists(request):

    get_task_id = request.data.get("task_id")
    task = TaskCard.objects.get(task_id=get_task_id)

    if not task:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    assigned_to_id = request.data.get("assigned_to")
    assigned_to_user = None
    if assigned_to_id:
        try:
            assigned_to_user = User.objects.get(user_id=assigned_to_id)
        except User.DoesNotExist:
            return Response({"error": "Assigned user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
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
       task_list = TaskList.objects.get(tasklist_id=task_list_id, created_by=request.user)
    except TaskList.DoesNotExist:
        return Response({"error": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user != task_list.created_by:
        return Response({"error": "You cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)

    task_image = TaskImage.objects.filter(tasks_lists_id=task_list).first()
    task_attachment = TaskAttachment.objects.filter(tasks_lists_id=task_list).first()

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
        return Response({"Status":"Successfull", "message": "Task list updated", "Task List Data": TaskListSerializer(task_list).data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#Tasks lists Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def tasks_lists_delete(request):

    get_task_list_id = request.data.get("task_list_id")

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
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Copy of task lists  OK
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_task_list(request):
    try:
        original_task_list_id = request.data.get("task_list_id")
        get_task_list = TaskList.objects.get(tasklist_id=original_task_list_id, created_by=request.user)

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
        task_list_id = request.data.get("task_list_id")
        new_task_card_id = request.data.get("new_task_card_id")

        task_list = TaskList.objects.get(tasklist_id=task_list_id, created_by=request.user)
        new_task_card = TaskCard.objects.get(task_id=new_task_card_id, created_by=request.user)
        
        task_list.task_card = new_task_card
        task_list.save()

        activity(request.user, f"{request.user.full_name} moved task list: {task_list.tasklist_title} to task card: {new_task_card.title}")

        return Response({"status": "successfull", "message": "Task list moved", "Task List Data": TaskListSerializer(task_list).data}, status=status.HTTP_200_OK)

    except TaskList.DoesNotExist:
        return Response({"status":"error", "message": "Task list not found"}, status=status.HTTP_404_NOT_FOUND)

    except TaskCard.DoesNotExist:
        return Response({"status":"error", "message": "New task card not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
