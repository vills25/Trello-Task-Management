from django.urls import path
from .views.authentication import *
from .views.board import *
from .views.task import * 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication Urls 
    path('register_user/', register_user),
    path('login_user/', login_user),
    path('forgot_password_sent_email/', forgot_password_sent_email),
    path('reset_password/', reset_password),
    path('update_profile/', update_profile),
    path('delete_profile/', delete_profile),
    path('search_view_all_users/', search_view_all_users),
    path('view_my_profile/', view_my_profile),
    path('show_activity/', show_activity),
    path('create_comment/', create_comment),
    path('edit_comment/', edit_comment),
    path('delete_comment/', delete_comment),

    # Board Urls
    path('create_board/', create_board),
    path('update_board/', update_board),
    path('delete_board/', delete_board),
    path('add_member_to_board/', add_member_to_board),
    path('remove_member_from_board/', remove_member_from_board),
    path('view_board_members/', view_board_members),
    path('get_my_board/', get_my_board),
    path('search_boards/', search_boards),
    path('star_board/', star_board),
    path('print_export_share/', print_export_share),
    path('share_invite/', share_invite),
    path('notifications/', notifications),

    # TaskCard Urls
    path('create_task/', create_task),
    path('update_task/', update_task),
    path('delete_task/', delete_task),
    path('search_tasks_by/', search_tasks_by),
    path('star_task_card/', star_task_card),
    path('copy_task_card/', copy_task_card),
    path('move_task_card_to_other_board/', move_task_card_to_other_board),
    # path('position/', position),

    # TaskList Urls
    path('create_task_lists/', create_task_lists),
    path('update_tasks_lists/', update_tasks_lists),
    path('tasks_lists_delete/', tasks_lists_delete),
    path('copy_task_list/', copy_task_list),
    path('move_task_list/', move_task_list),
    path('sort_task_lists/', sort_task_lists),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)