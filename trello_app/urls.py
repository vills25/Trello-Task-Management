from django.urls import path
from .views.authentication import *
from .views.board import *
from .views.task import * 

urlpatterns = [
    # Authentication Urls 
    path('register_user/', register_user),
    path('login_user/', login_user),
    # path('logout_user/', logout_user),
    path('forgot_password_sent_email/', forgot_password_sent_email),
    path('reset_password/', reset_password),
    path('update_profile/', update_profile),
    path('delete_profile/', delete_profile),
    path('view_all_users/', view_all_users),
    path('view_my_profile/', view_my_profile),
    
    # Board Urls
    path('create_board/', create_board),
    path('update_board/', update_board),
    path('delete_board/', delete_board),
    path('add_member_to_board/', add_member_to_board),
    path('remove_member_from_board/', remove_member_from_board),
    path('view_board_members/', view_board_members),
    path('get_my_board/', get_my_board),
    path('search_boards/', search_boards),

    # Task Urls
    path('task_get/', task_get),
    path('create_task/', create_task),
    path('update_task/', update_task),
    path('delete_task/', delete_task),
    path('mark_task_complete/', mark_task_complete),
    path('add_media_files/', add_media_files),
    path('delete_task_mediafile/', delete_task_mediafile),
    path('replace_task_mediafiles/', replace_task_mediafiles),
    path('search_tasks/', search_tasks),
]    