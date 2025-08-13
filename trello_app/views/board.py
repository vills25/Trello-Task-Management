from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import Board, User, TaskCard, TaskAttachment, TaskImage, TaskList
from trello_app.serializers import BoardSerializer, TaskListSerializer
from datetime import date, timedelta
from django.utils import timezone

# Create User Board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_board(request):
    try:
        with transaction.atomic():
            data = request.data
            board = Board.objects.create(
                title=data.get("title"),
                description=data.get("description", ""),
                visibility=data.get("visibility", "private"),
                created_by=request.user
            )
            board.members.add(request.user)
            serializer = BoardSerializer(board)
            return Response({"message": "Board created successfully", "Board Data": serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#Update User Board
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_board(request):
    try:
        board_id = request.data.get("board_id")
        board = Board.objects.get(board_id=board_id) 
    except Board.DoesNotExist:
        return Response({"Error": "Board not found"}, status= status.HTTP_404_NOT_FOUND)
    
    if not board_id:
        return Response({"Error": "board_id is required"},status=status.HTTP_400_BAD_REQUEST)
    
    data = request.data
    try:
         with transaction.atomic():

            if 'title' in data:
                board.title = data['title'] 
       
            if 'description' in data:
                board.description = data['description']

            if 'visibility' in data :
                board.visibility =  data['visibility']     
            
            board.save()
            serializer = BoardSerializer(board)
            return Response({"message": "Board Updated successfully", "Board Data": serializer.data}, status=status.HTTP_200_OK)
         
    except Board.DoesNotExist:
        return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Delete User Board
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_board(request):
    try: 
        board_id = request.data.get("board_id")
        board = Board.objects.get(board_id=board_id, created_by=request.user)
        board.delete()
        return Response({"message": "Board deleted successfully"}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)


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

        return Response({"message": f"{user.count()} added to board"}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"error": "Board not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Remove memeber from board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_member_from_board(request):
    try:
        board_id = request.data.get("board_id")
        user_email = request.data.get("email")

        board = Board.objects.get(board_id=board_id, created_by=request.user)
        user = User.objects.get(email=user_email)

        board.members.remove(user)
        return Response({"message": f"{user.username} removed from board"}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"error": "Board not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# View Board members
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_board_members(request):
    try:
        board_id = request.data.get("board_id")
        board = Board.objects.get(board_id=board_id)

        if request.user not in board.members.all():
            return Response({"error": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        members_data = []
        for member in board.members.all():
            members_data.append({
                "user_id": member.user_id,
                "username": member.username,
                "email": member.email
            })
        return Response({"Members in your Task Board":members_data}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"error": "Task Board not found"}, status=status.HTTP_404_NOT_FOUND)


# #View for full board details
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_my_board(request):
    try:
        
        board_id = request.data.get('board_id')

        if not board_id:
            boards = Board.objects.filter(members=request.user).order_by('-is_starred'  )

            serializer = BoardSerializer(boards, many=True)
            return Response({"Message":"Success","Board data": serializer.data}, status=status.HTTP_200_OK)

        try:
            board = Board.objects.get(board_id=board_id, members=request.user)
        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        members = board.members.all()
        
        board_data = {
            "board_id": board.board_id,
            "title": board.title,
            "description": board.description,
            "visibility": board.visibility,
            "created_by":  board.created_by.full_name if board.created_by else "Unknown",
            "created_at": board.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            "updated_by": board.updated_by.full_name if board.updated_by else "Unknown",
            "updated_at": board.updated_at.strftime("%d-%m-%Y %H:%M:%S"),
            "members": [
                {   
                    "user_id": member.user_id,
                    "full_name": member.full_name
                }
                for member in members
            ],

            "Tasks Cards": [] 
        }
        
        tasks = TaskCard.objects.filter(board=board).select_related('created_by', 'updated_by', 'assigned_to').order_by('-is_starred')
        
        # Filter Functionality
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(weeks=1)
        month = today + timedelta(days=30)
        filters = request.data

        if filters.get('assigned_to_me'):
             tasks = tasks.filter(assigned_to = request.user)

        if 'complated' in filters:
             if filters['completed']:
                  tasks = tasks.filter(status = 'completed')
             else: tasks = tasks.exclude(status='completed') 

        if filters.get('no_due'):
             tasks = tasks.filter(due_date__isnull = True)

        if filters.get('overdue'):
             tasks = tasks.filter(due_date__lt=today)

        if filters.get('due_today'):
            tasks = tasks.filter(due_date=today)

        if filters.get('due_tomorrow'):
            tasks = tasks.filter(due_date=tomorrow)

        if filters.get('due_next_week'):
            tasks = tasks.filter(due_date__range=[next_week, month])

        if filters.get('due_on_this_month'):
            tasks = tasks.filter(due_date__month=today.month)


        for task in tasks:
            task_images = TaskImage.objects.filter(task_card=task)
            task_attachments = TaskAttachment.objects.filter(task_card=task)
            tasks_lists = TaskList.objects.filter(task_card=task)

            board_data["Tasks Cards"].append({
                "Task_id": task.task_id,
                "Title": task.title,
                "Description": task.description,
                "Due_date": task.due_date,
                "Assigned_to": task.assigned_to.full_name if task.assigned_to else "Unassigned",
                "Created_by": task.created_by.full_name,
                "Created_at": task.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                "Updated_by": task.updated_by.full_name if task.updated_by else "None",   
                "Updated_at": task.updated_at.strftime("%d-%m-%Y %H:%M:%S"),   
                "media_files": {
                    "images": [
                        {
                            "id": image.task_image_id,
                            "file_url": image.task_image.url,
                        } for image in task_images
                    ],

                    "attachments": [
                        {   
                            "id": attachment.task_attachment_id,
                            "file_url": attachment.task_attachment.url,
                        } for attachment in task_attachments
                    ]
                },
                "task_lists": TaskListSerializer(tasks_lists, many=True).data
            })

        return Response({"message": "User data fatched Successfull", "Taskboard data": board_data}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"error": "Board not found"}, status= status.HTTP_404_NOT_FOUND)


# Search Board members.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_boards(request):   
    try:
        data = request.data

        board_id = data.get('board_id')
        title = data.get('title','')
        description = data.get('descriptionitle','')
        visibility= data.get('visibility','')
        created_by= data.get('created_by','')
        updated_by= data.get('updated_by','')
        members= data.get('members','')

        queryset = Board.objects.filter().order_by('-is_starred')

        if board_id:
                queryset = queryset.filter(pk=board_id)

        if title:
                queryset = queryset.filter(title__icontains=title)

        if description:
                queryset = queryset.filter(description__icontains=description)

        if visibility:
                queryset = queryset.filter(visibility__icontains=visibility)

        if created_by:
                queryset = queryset.filter(created_by__icontains=created_by)

        if updated_by:
                queryset = queryset.filter(updated_by__icontains=updated_by)

        if members:
                queryset = queryset.filter(members__icontains=members)

        if not queryset.exists():
                return Response({"message": "No matching Boards found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BoardSerializer(queryset, many=True)
        return Response({"Task Board Data": serializer.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Give Star To Board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_board(request):
    board_id = request.data.get('board_id')
    try:
        board = Board.objects.get(board_id=board_id, members=request.user)
        board.is_starred = not board.is_starred
        board.save()
        return Response({"message": "Board star status updated", "is_starred": board.is_starred})
    except Board.DoesNotExist:
        return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
