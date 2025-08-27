from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import *
from trello_app.serializers import *
from datetime import date, timedelta
from django.utils import timezone
from .authentication import activity

# Create User Board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_board(request):
    try:
        with transaction.atomic():
            data = request.data
            members_emails = data.get("members", [])
            
            board = Board.objects.create(
                title=data.get("title"),
                description=data.get("description", ""),
                visibility=data.get("visibility", "private"),
                created_by=request.user
            )
            board.members.add(request.user)
            
            if members_emails:
                extra_members = User.objects.filter(email__in=members_emails)
                board.members.add(*extra_members)
                
            serializer = BoardSerializer(board)
            activity(request.user, f"{request.user.full_name} created Board: {board.title}")
            return Response({"status":"success", "message": "Board created successfully", "Board Data": serializer.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#Update User Board
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_board(request):
    try:
        board_id = request.data.get("board_id")
        if not board_id:
            return Response({"status":"error", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        board = Board.objects.get(board_id=board_id) 
    except Board.DoesNotExist:
        return Response({"status":"error", "message": "Board not found"}, status= status.HTTP_404_NOT_FOUND)
    
    if not board_id:
        return Response({"status":"error", "message": "board_id is required"},status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    try:
         with transaction.atomic():

            if 'title' in data:
                board.title = data['title'] 
    
            if 'description' in data:
                board.description = data['description']

            if 'visibility' in data :
                board.visibility =  data['visibility']   

            board.updated_by = request.user
            board.save()
            activity(request.user, f'{request.user.full_name} updated board: {board.title}')
            serializer = BoardSerializer(board, many = True)
            return Response({"status":"success", "message": "Board Updated successfully", "Board Data": serializer.data}, status=status.HTTP_200_OK)

    except Board.DoesNotExist:
        return Response({"status":"error", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Delete User Board
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_board(request):
    try:
        board_id = request.data.get("board_id")
        if not board_id:
            return Response({"status":"error", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        board = Board.objects.get(board_id=board_id, created_by=request.user)

        board.delete()
        activity(request.user, f"{request.user.full_name} Deleted Board : {board.title}")

        return Response({"status":"success", "message": "Board deleted successfully"}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"status":"error", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)


# Add/Assign Member to Board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_to_board(request):
    try:
        board_id = request.data.get("board_id")
        user_emails = request.data.get("email")

        board = Board.objects.get(board_id=board_id, created_by=request.user)
        user = User.objects.filter(email__in=user_emails)

        board.members.add(*user)
        activity(request.user, f"{request.user.username} added members to board, title: {board.title}")

        return Response({"status":"success", "message": f"{user.count()} members added to board"}, status=status.HTTP_200_OK)
    
    except Board.DoesNotExist:
        return Response({"status":"error", "message": "Board not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    
    except User.DoesNotExist:
        return Response({"status":"error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Remove member from board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_member_from_board(request):
    try:
        board_id = request.data.get("board_id")
        user_email = request.data.get("email")

        board = Board.objects.get(board_id=board_id, created_by=request.user)
        user = User.objects.get(email=user_email)

        board.members.remove(user)

        activity(request.user, f"{request.user.full_name} removed {user.username} from board, title: {board.title}")
        
        return Response({"status":"success", "message": f"{user.username} removed from board"}, status=status.HTTP_200_OK)
    
    except Board.DoesNotExist:
        return Response({"status":"error", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({"status":"error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# View Board members
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_board_members(request):
    try:
        board_id = request.data.get("board_id")
        if not board_id:
            return Response({"status":"error", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)
        board = Board.objects.get(board_id=board_id)

        if request.user not in board.members.all():
            return Response({"status":"error", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        members_data = []
        for member in board.members.all():
            members_data.append({
                "user_id": member.user_id,
                "username": member.username,
                "email": member.email
            })
        activity(request.user, f"{request.user.full_name} viewed members of board, Title: {board.title}")
        return Response({"status":"success", "Members in your Board":members_data}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"status":"error", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#View for full board details
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_my_board(request):

    try:        
        board_id = request.data.get('board_id')

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        this_week =  today - timedelta(days=today.weekday())
        next_week = today + timedelta(weeks=1)
        month = today + timedelta(days=30)

        if not board_id:
            boards = Board.objects.filter(members=request.user).order_by('-is_starred')

            # Board filters
            if request.data.get('board_title'):
                boards = boards.filter(title__icontains=request.data['board_title'])

            if request.data.get('board_description'):
                boards = boards.filter(description__icontains=request.data['board_description'])

            if request.data.get('no_members'):
                boards = boards.filter(members__isnull=True)
            
            boards = boards.distinct()
            activity(request.user, f"{request.user.full_name} viewed boards")

            serializer = BoardSerializer(boards, many=True)
            return Response({"status":"success", "Board data": serializer.data}, status=status.HTTP_200_OK)

        try:
            board = Board.objects.get(board_id=board_id, members=request.user)
        except Board.DoesNotExist:
            return Response({"status":"error", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        members = board.members.all()
        
        board_data = {
            "board_id": board.board_id,
            "title": board.title,
            "description": board.description,
            "visibility": board.visibility,
            "created_by": board.created_by.full_name if board.created_by else "Unknown",
            "created_at": board.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            "updated_by": board.updated_by.full_name if board.updated_by else "Unknown",
            "updated_at": board.updated_at.strftime("%d-%m-%Y %H:%M:%S"),
            "members": [{"user_id": m.user_id, "full_name": m.full_name} for m in members],
            "Tasks Cards": []
        }

        tasks = TaskCard.objects.filter(board=board).select_related('created_by', 'updated_by').order_by('-is_starred')

        # TaskCard filters

        if 'completed' in request.data:
            if request.data['completed']:
                tasks = tasks.filter(is_completed='completed')
            else:
                tasks = tasks.exclude(is_completed='completed')
        
        if request.data.get('task_title'):
            tasks = tasks.filter(title__icontains=request.data['task_title'])

        if request.data.get('task_description'):
            tasks = tasks.filter(description__icontains=request.data['task_description'])

        if request.data.get('created_by'):
            tasks = tasks.filter(created_by__full_name__icontains=request.data['created_by'])

        if request.data.get('is_starred'):
            tasks = tasks.filter(is_starred=request.data['is_starred'])

        # TaskList filters
        if request.data.get('task_list_title'):
            tasks = tasks.filter(task_lists__tasklist_title__icontains=request.data['task_list_title'])

        if request.data.get('task_list_description'):
            tasks = tasks.filter(task_lists__tasklist_description__icontains=request.data['task_list_description'])

        if request.data.get('assigned_to'):
            tasks = tasks.filter(assigned_to__full_name__icontains=request.data['assigned_to'])

        if request.data.get('priority'):
            tasks = tasks.filter(task_lists__priority=request.data['priority'])

        if request.data.get('label_color'):
            tasks = tasks.filter(task_lists__label_color=request.data['label_color'])

        if request.data.get('no_due'):
            tasks = tasks.filter(task_lists__due_date__isnull=True)

        if request.data.get('overdue'):
            tasks = tasks.filter(task_lists__due_date__lt=today)

        if request.data.get('due_today'):
            tasks = tasks.filter(task_lists__due_date=today)

        if request.data.get('due_tomorrow'):
            tasks = tasks.filter(task_lists__due_date=tomorrow)

        if request.data.get('due_next_week'):
            tasks = tasks.filter(task_lists__due_date__range=[next_week, month])

        if request.data.get('due_on_this_month'):
            tasks = tasks.filter(task_lists__due_date__month=today.month)

        if request.data.get('due_on_this_week'):
            tasks = tasks.filter(task_lists__due_date__range=[this_week, next_week])

        tasks = tasks.distinct()
        url_path = request.META.get('HTTP_HOST', '')

        for task in tasks:
            tasks_lists = TaskList.objects.filter(task_card=task)
            comments = Comment.objects.filter(user= request.user)
            
            task_list_data = []
            for tlist in tasks_lists:
                list_images = TaskImage.objects.filter(tasks_lists_id=tlist)
                list_attachments = TaskAttachment.objects.filter(tasks_lists_id=tlist)
                list_comments = Comment.objects.filter(task_list=tlist)

                task_list_data.append({
                    "tasklist_id": tlist.tasklist_id,
                    "tasklist_title": tlist.tasklist_title,
                    "tasklist_description": tlist.tasklist_description,
                    "priority": tlist.priority,
                    "label_color": tlist.label_color,
                    "due_date": tlist.due_date.strftime("%d-%m-%Y") if tlist.due_date else None,
                    "comments": [
                    {
                        "comment": comment.comment_text,
                        "commented_by": comment.user.full_name if comment.user else "Unknown"
                    }
                    for comment in list_comments
                ],
                    "Media_files": {
                        "Images": [{"image_url": f'http://{url_path}{img.task_image.url}'} for img in list_images],
                        "Attachments": [{"attachment_url": f'http://{url_path}{att.task_attachment.url}'} for att in list_attachments]
                    }
                })
            
            board_data["Tasks Cards"].append({
                "Task_id": task.task_id,
                "Title": task.title,
                "Description": task.description,
                "Created_by": task.created_by.full_name,
                "Created_at": task.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                "Updated_by": task.updated_by.full_name if task.updated_by else "None",
                "Updated_at": task.updated_at.strftime("%d-%m-%Y %H:%M:%S"),
                "Task Lists": task_list_data,
            })
        activity(request.user, f"{request.user.full_name} performed action on board, board title: {board.title}")
        return Response({"status":"success", "Board data": board_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Search Board members.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_boards(request):   
    try:
        data = request.data
        queryset = Board.objects.filter(members = request.user).order_by('-is_starred')

        if data.get('board_id'):
            queryset = queryset.filter(pk=data['board_id'])
        if data.get('title'):
            queryset = queryset.filter(title__icontains=data['title'])
        if data.get('description'):
            queryset = queryset.filter(description__icontains=data['description'])
        if data.get('visibility'):
            queryset = queryset.filter(visibility__icontains=data['visibility'])
    
        if not queryset.exists():
            return Response({"status":"error", "message": "No matching Boards found"}, status=status.HTTP_404_NOT_FOUND)

        activity(request.user, f"{request.user.full_name} Searched Boards")
        serializer = BoardSerializer(queryset, many=True)
        return Response({"status":"success", "Board Data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Give Star To Board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_board(request):
    board_id = request.data.get('board_id')
    if not board_id:
        return Response({"status":"error", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        board = Board.objects.get(board_id=board_id, members=request.user)
        board.is_starred = not board.is_starred
        board.save()

        activity(request.user, f"{request.user.full_name} updated Star status of Board: {board.title} - {'Starred' if board.is_starred else 'Unstarred'}")

        return Response({"status":"success", "message": "Board star status updated", "is_starred": board.is_starred})

    except Board.DoesNotExist:
        return Response({"status":"error", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

