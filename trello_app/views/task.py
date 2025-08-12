from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import User, Board,TaskCard, TaskAttachment, TaskImage, TaskList
from trello_app.serializers import TaskCardSerializer


# Search Task Cards    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_tasks(request):
    try:
        data = request.data

        task_id = data.get('task_id')
        title = data.get('title')
        board = data.get('board','')
        description = data.get('description','')
        due_date= data.get('due_date','')
        created_by= data.get('created_by','')
        is_completed= data.get('is_completed','')

        queryset = TaskCard.objects.all()

        if task_id:
                queryset = queryset.filter(pk=task_id)

        if title:
            queryset = queryset.filter(title__icontains = title)

        if board:
                queryset = queryset.filter(board__title__icontains=board)

        if description:
                queryset = queryset.filter(description__icontains=description)

        if due_date:
                queryset = queryset.filter(due_date__icontains=due_date)

        if created_by:
                queryset = queryset.filter(created_by__icontains=created_by)

        if is_completed:
                queryset = queryset.filter(is_completed__icontains=is_completed)

        if not queryset.exists():
                return Response({"message": "No matching Tasks found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskCardSerializer(queryset, many=True)
        return Response({"Task Data": serializer.data}, status=status.HTTP_200_OK)

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
                created_by=request.user,
                assigned_to=assigned_to_user
            )
                
            for img in request.FILES.getlist("images"):
                TaskImage.objects.create(task_card=task, task_image=img)

            for file in request.FILES.getlist("attachments"):
                TaskAttachment.objects.create(task_card=task, task_attachment=file)
            
            subtasks = data.get('task_lists', [])
            for sub in subtasks:
                if sub.get("tasklist_title") and sub.get("tasklist_description"):
                        TaskList.objects.create(
                            task_card=task,
                            tasklist_title=sub.get("tasklist_title"),
                            tasklist_description=sub.get("tasklist_description"),
                            created_by=request.user,
                        )

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

            if "subtasks" in data:
                subtasks = request.data.get('subtasks', [])
                for sub in subtasks:
                    if "tasklist_id" in sub:  
                        try:
                            task_list = TaskList.objects.get(tasklist_id=sub['tasklist_id'], task_card=task)
                            task_list.tasklist_title = sub.get('tasklist_title', task_list.tasklist_title)
                            task_list.tasklist_description = sub.get('tasklist_description', task_list.tasklist_description)
                            task_list.is_completed = sub.get('is_completed', task_list.is_completed)
                            task_list.updated_by = request.user
                            task_list.save()
                        except TaskList.DoesNotExist:
                            continue
                    else:
                        TaskList.objects.create(
                            task_card=task,
                            tasklist_title=sub.get('tasklist_title', ''),
                            tasklist_description=sub.get('tasklist_description', ''),
                            is_completed=sub.get('is_completed', False),
                            created_by=request.user
                        )

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


