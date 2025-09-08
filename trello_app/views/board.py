from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction   # For atomic DB transactions (to ensures rollback if any part fails)
from trello_app.models import *
from trello_app.serializers import *
from datetime import date, timedelta
from django.utils import timezone
from .authentication import activity
from django.conf import settings  
from django.core.mail import send_mail   # Django’s built-in email function
from django.db.models import Q
from .utils import *

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
            # add board creator as a default member
            board.members.add(request.user)

            # Add extra members if provided
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
            return Response({"status":"fail", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        board = Board.objects.get(board_id=board_id) 
    except Board.DoesNotExist:
        return Response({"status":"fail", "message": "Board not found"}, status= status.HTTP_404_NOT_FOUND)
    # Only creator can update
    if board.created_by != request.user:
        return Response({"status": "fail", "message": "you can not update other's boards."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    try:
         with transaction.atomic():

            # Update board fields if provided
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
        return Response({"status":"fail", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Delete User Board
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_board(request):
    try:
        board_id = request.data.get("board_id")
        if not board_id:
            return Response({"status":"fail", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Check board belongs to requesting user
        board = Board.objects.get(board_id=board_id, created_by=request.user)
        if board.created_by != request.user:
            return Response({"status": "fail", "message": "you can not delete the board"}, status=status.HTTP_403_FORBIDDEN)

        board.delete()
        activity(request.user, f"{request.user.full_name} Deleted Board : {board.title}")

        return Response({"status":"success", "message": "Board deleted successfully"}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"status":"fail", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)


# Add/Assign Member to Board, Only superuser or board creator
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_to_board(request):
    try:
        board_id = request.data.get("board_id")
        user_emails = request.data.get("email")
        
        if not board_id or not user_emails:
            return Response({"status": "fail", "message": "Please provide board_id and user emails"}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_superuser and not Board.objects.filter(board_id=board_id, created_by=request.user).exists():
            return Response({"status": "fail", "message": "Only superusers or board admins can add members to boards"},
                              status=status.HTTP_403_FORBIDDEN)

        board = Board.objects.get(board_id=board_id, created_by=request.user)

        # Clean email list
        user_emails = [e.strip().lower() for e in user_emails]

        # Find existing users
        found_users = User.objects.filter(email__in=user_emails)
        found_emails = set(found_users.values_list("email", flat=True))
        not_found = [e for e in user_emails if e not in found_emails]

        # Add found users
        if found_users:
            board.members.add(*found_users)
            activity(request.user, f"{request.user.username} added members to board, title: {board.title}")

        return Response({"status": "success","message": f"{found_users.count()} members added","not_found": not_found}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"status":"fail", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Remove member from board
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_member_from_board(request):
    try:
        board_id = request.data.get("board_id")
        user_email = request.data.get("email")

        board = Board.objects.get(board_id=board_id, created_by=request.user)
        user = User.objects.get(email=user_email)

        if not request.user.is_superuser and not board.created_by == request.user:
            return Response({"status": "fail", "message": "only superusers or board admins can remove members from boards"},
                            status=status.HTTP_403_FORBIDDEN)

        board.members.remove(user)

        activity(request.user, f"{request.user.full_name} removed {user.username} from board, title: {board.title}")
        
        return Response({"status":"success", "message": f"{user.username} removed from board"}, status=status.HTTP_200_OK)
    
    except Board.DoesNotExist:
        return Response({"status":"fail", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({"status":"fail", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# View Board members
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_board_members(request):
    try:
        board_id = request.data.get("board_id")
        if not board_id:
            return Response({"status":"fail", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)
        board = Board.objects.get(board_id=board_id)

        if request.user not in board.members.all():
            return Response({"status":"fail", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        members_data = []
        for member in board.members.all():
            members_data.append({
                "user_id": member.user_id,
                "username": member.username,
                "email": member.email
            })
        activity(request.user, f"{request.user.full_name} viewed members of board, Title: {board.title}")
        return Response({"status":"success", "message":"Members Found" ,"Members in your Board":members_data}, status=status.HTTP_200_OK)
    except Board.DoesNotExist:
        return Response({"status":"fail", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Get Full Board Data with Filter/Search functionality
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_my_board(request):

    try:        
        board_id = request.data.get('board_id')
        if not board_id:
            return Response({"status": "fail", "message": "Please provide board_id"}, status=status.HTTP_400_BAD_REQUEST)

        if not board_id:
            boards = Board.objects.filter(members=request.user).order_by('-is_starred')

            if request.data.get('visibility'):
                boards = boards.filter(visibility__icontains = request.data.get('visibility'))
                
            if request.data.get('no_members'):
                boards = boards.filter(members__isnull=True)
            
            boards = boards.distinct()  #Remove Duplicate
            activity(request.user, f"{request.user.full_name} viewed boards")

            serializer = BoardSerializer(boards, many=True)
            return Response({"status":"success", "message": "Board filtered","Board data": serializer.data}, status=status.HTTP_200_OK)

        try:
            board = Board.objects.get(board_id=board_id, members=request.user) 
        except Board.DoesNotExist:
            return Response({"status":"fail", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        members = board.members.all()
        
        # board_data >> Tasks Cards
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

        # Get Board with TaskCard based filter
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

        # Get Board with TaskList based filter
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

        # DateTime based Filter
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        this_week =  today - timedelta(days=today.weekday())
        next_week = today + timedelta(weeks=1)
        month = today + timedelta(days=30)

        if request.data.get('no_due'):
            tasks = tasks.filter(task_lists__due_date__isnull=True)

        if request.data.get('overdue'):
            tasks = tasks.filter(task_lists__due_date__lt=today)

        if request.data.get('due_today'):
            tasks = tasks.filter(task_lists__due_date=today)

        if request.data.get('due_tomorrow'):
            tasks = tasks.filter(task_lists__due_date=tomorrow)

        if request.data.get('due_on_this_week'):
            tasks = tasks.filter(task_lists__due_date__range=[this_week, next_week])

        if request.data.get('due_next_week'):
            tasks = tasks.filter(task_lists__due_date__range=[next_week, month])

        if request.data.get('due_on_this_month'):
            tasks = tasks.filter(task_lists__due_date__month=today.month)

        url_path = request.META.get('HTTP_HOST', '') # Get Host http://127.0.0.1:8000
        tasks = tasks.distinct() # Remove duplicate

        # Get task from tasks through loop and add into "task_list_data = []"
        for task in tasks:
            tasks_lists = TaskList.objects.filter(task_card=task)
            task_list_data = []
            
            for tasklist in tasks_lists:
                print("========== BOARD IMAGES ===========", tasklist.images)
                print("========== BOARD ATTACHMENT ===========", tasklist.attachments)
                task_list_data.append({
                    "tasklist_id": tasklist.tasklist_id,
                    "tasklist_title": tasklist.tasklist_title,
                    "tasklist_description": tasklist.tasklist_description,
                    "priority": tasklist.priority,
                    "label_color": tasklist.label_color,
                    "due_date": tasklist.due_date.strftime("%d-%m-%Y") if tasklist.due_date else None,
                    "is_completed": tasklist.is_completed,
                    "assigned_to": tasklist.assigned_to.full_name if tasklist.assigned_to else "Unassigned",
                    "Media_files": {
                        "Images": [f"http://{url_path}{img}" for img in tasklist.images] if tasklist.images else [],
                        "Attachments": [f"http://{url_path}{att}" for att in tasklist.attachments] if tasklist.attachments else [],
                    },
                    "comments": TaskListSerializer().get_comments(tasklist),
                    "checklist_progress": TaskListSerializer().get_checklist_progress(tasklist),
                    "checklist_items": tasklist.checklist_items,
                })

            # Append "TaskCard" along with TaskList in to Board
            board_data["Tasks Cards"].append({
                "Task_id": task.task_id,
                "Title": task.title,
                "Description": task.description,
                "Created_by": task.created_by.full_name,
                "Created_at": task.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                "Updated_by": task.updated_by.full_name if task.updated_by else "None",
                "Updated_at": task.updated_at.strftime("%d-%m-%Y %H:%M:%S"),
                "Task Lists": task_list_data, # Add "Tasks Lists" in to Card
            })
        activity(request.user, f"{request.user.full_name} performed action on board, board title: {board.title}")
        return Response({"status":"success","message": "Board fetched", "Board data": board_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Search Board members.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_boards(request):   
    try:
        data = request.data
        queryset = Board.objects.filter(members = request.user).order_by('-is_starred')

        if not request.user in queryset.first().members.all():
            return Response({"status": "fail", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        if data.get('board_id'):
            queryset = queryset.filter(pk=data['board_id'])
        if data.get('title'):
            queryset = queryset.filter(title__icontains=data['title'])
    
        if not queryset.exists():
            return Response({"status":"fail", "message": "No matching Boards found"}, status=status.HTTP_404_NOT_FOUND)

        activity(request.user, f"{request.user.full_name} Searched Boards")
        serializer = BoardSerializer(queryset, many=True)
        return Response({"status":"success", "message": "Board fetched","Board Data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Toggle star/unstar on a board for the current user.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_board(request):
    board_id = request.data.get('board_id')
    if not board_id:
        return Response({"status":"fail", "message":"please enter board_id"}, status=status.HTTP_400_BAD_REQUEST)
     
    try:
        board = Board.objects.get(board_id=board_id, members=request.user)
        if not request.user in board.members.all():
            return Response({"status": "fail", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)
        
        board.is_starred = not board.is_starred
        board.save()

        activity(request.user, f"{request.user.full_name} updated Star status of Board: {board.title} - {'Starred' if board.is_starred else 'Unstarred'}")

        return Response({"status":"success", "message": "Board star status updated", "is_starred": board.is_starred})

    except Board.DoesNotExist:
        return Response({"status":"fail", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Share Board/Invite member to board via email, generate link and send email
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_invite(request):
    try:
        board_id = request.data.get("board_id")
        email = request.data.get("email")
        board = Board.objects.get(board_id=board_id)
        user = User.objects.get(email=email)

        if not board_id or not email:
            return Response({"status":"fail", "message":"please provide board_id and email"}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user in board.members.all():
            return Response({"status": "fail", "message": "You are not a member of this board"}, status=status.HTTP_403_FORBIDDEN)

        # Get board__id from request and email from logged in user and sent email using django's built-in send_mail() function
        link = f"http://trellotaskmanagement.com/invite?board_id={board.board_id}&email={user.email}"
        
        # django's built-in send_mail() function
        send_mail(
            subject=f"link for join board: {board.title}",
            message=f"click the link for join the board: {link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],)
        
        activity(request.user, f"{request.user.full_name} invited {user.username} to board, Title: {board.title}")
        
        return Response({"status":"success", "message": f"Invitation sent to {email}", "invitation_link": link}, status=status.HTTP_200_OK)
    
    except Board.DoesNotExist:
        return Response({"status":"fail", "message": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({"status":"fail", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status":"error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# notification for remind tasks due and upcoming deadlines
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request):
    user = request.user 

    # Get today's date and calculate upcoming date (2 days from now)
    today = timezone.now().date()
    upcoming = today + timedelta(days=2)

    # Query for upcoming tasks that are either assigned to the user or belong to boards where the user is a member
    upcoming_tasks = TaskList.objects.filter(
        Q(assigned_to=user) | Q(task_card__board__members=user), due_date=upcoming, is_completed=False).distinct().order_by('due_date') # Remove duplicates and order by due date

    # Send reminder emails
    for task in upcoming_tasks:
         # Check if the task is assigned to someone with an email address
        if task.assigned_to and task.assigned_to.email:
            # Create email subject and message
            subject = f"Reminder: Task '{task.tasklist_title}' is due soon"
            message = (
                f"Hello {task.assigned_to.username},\n\n"
                f"Your task '{task.tasklist_title}' is due on {task.due_date}.\n"
                f"Please complete it before the deadline."
            )

    send_mail(subject, message, None, [task.assigned_to.email], fail_silently=False ) 
    # fail_silently=False -->> Raise errors if email fails to send

    activity(request.user, f"{request.user.username} viewed notifications")

    serializer = TaskListSerializer(upcoming_tasks, many=True)
    return Response({"status": "success", "message":"Notification Sent Successfully","data": serializer.data}, status=status.HTTP_200_OK)