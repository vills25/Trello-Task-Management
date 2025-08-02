from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import Board, User, TaskCard, TaskAttachment, TaskImage

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
            return Response({
                "message": "Board created successfully",
                "board_id": board.board_id,
                "title": board.title,
                "visibility": board.visibility
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#View for full board details
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_board(request):
    try:
        board = request.data.get('board_id')
        if not board:
            return Response({"error": "Board ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    except Board.DoesNotExist:
        return Response({"error": "Board not found"}, status= status.HTTP_404_NOT_FOUND)

    board = Board.objects.get(board_id=board, members=request.user)

    members = board.members.all()
    tasks = TaskCard.objects.filter(board=board).select_related('created_by', 'updated_by', 'assigned_to')

    board_data = {
        "board_id": board.board_id,
        "title": board.title,
        "description": board.description,
        "visibility": board.visibility,

        "created_at": board.created_at,
        "created_by": {
            "user_id": board.created_by.user_id,
            "full_name": board.created_by.full_name
        },

        "updated_at": board.updated_at,
        "updated_by": {
            "user_id": board.updated_by.user_id,
            "full_name": board.updated_by.full_name
        } if board.updated_by else None,

        "members": [
            {   
                "user_id": member.user_id,
                "full_name": member.full_name
            }
            for member in members
        ],

        "Tasks Cards": [] 
    }
    
    for task in tasks:
        task_images = TaskImage.objects.filter(task_card=task)
        task_attachments = TaskAttachment.objects.filter(task_card=task)

        board_data["Tasks Cards"].append({
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "Task Status": task.is_completed,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,

            "created_by": {
                "user_id": task.created_by.user_id,
                "full_name": task.created_by.full_name
            },

            "updated_by": {
                "user_id": task.updated_by.user_id,
                "full_name": task.updated_by.full_name
            } if task.updated_by else None,

            "assigned_to": {
                "user_id": task.assigned_to.user_id,
                "full_name": task.assigned_to.full_name
            } if task.assigned_to else None,
            
            "media_files": {
                "images": [
                    {
                        "id": image.task_image_id,
                        "file_url": image.task_image.url,

                    } for image in task_images
                ],
                
                "attachments": [
                    {   "id": attachment.task_attachment_id,
                        "file_url": attachment.task_attachment.url,
                    } for attachment in task_attachments
                ]
            }
        })

    return Response({"message": "User data fatched Successfull", "Taskboard data": board_data}, status=status.HTTP_200_OK)


#Update User Board
@api_view(['PUT', 'PATCH'])
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

            return Response({
                "message": "Board updated successfully",
                "board_id": board.board_id,
                "title": board.title,
                "description": board.description,
                "visibility": board.visibility
    
            }, status=status.HTTP_200_OK)
    
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

# Clear User Board (remove all lists cards from board but keep board)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_board(request):
    try:
        board_id = request.data.get("board_id")
        board = Board.objects.get(board_id=board_id, created_by=request.user)
    
        board.objects.all().delete()
    
        return Response({"message": "Board cleared successfully"}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)


# Add/Assign Member to Board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_to_board(request):
    try:
        board_id = request.data.get("board_id")
        user_email = request.data.get("email")

        board = Board.objects.get(board_id=board_id, created_by=request.user)
        user = User.objects.get(email=user_email)

        board.members.add(user)

        return Response({"message": f"{user.username} added to board"}, status=status.HTTP_200_OK)
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

# User can search his Boards if he created more than one 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_boards(request):
    search_board = request.data.get("board_id", "")
    boards = Board.objects.filter(title__icontains=search_board, members=request.user)
    data = []
    for b in boards:
        data.append({
            "board_id": b.board_id,
            "title": b.title,
            "visibility": b.visibility
        })
    return Response(data, status=status.HTTP_200_OK)

