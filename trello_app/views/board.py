from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from trello_app.models import Board, User


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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_board(request):
    try:
        board_id = request.data.get("board_id")
        board = Board.objects.get(board_id=board_id) 
    except Board.DoesNotExist:
        return Response({"Error": "Board not found"}, status= status.HTTP_404_NOT_FOUND)
    data = request.data
    if not data.get('board_id'):
        return Response({"Error": "board_id is required"})
    
    try:
        board.title = data['title']
        board.description = data['description']
        board.visibility = data['visibility']
        board.save()

        return Response({
            "message": "Board updated successfully",
            "board_id": board.board_id,
            "title": board.title,
            "visibility": board.visibility
        }, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"error": "Board not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

