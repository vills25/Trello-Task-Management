from django.urls import path
from .views.authentication import *
from .views.board import *
from .views.task import * 

urlpatterns = [
    # Authentication Urls 
    path('register_user/', register_user),
    path('login_user/', login_user),
    path('forgot_password_sent_email/', forgot_password_sent_email),
    path('reset_password/', reset_password),
    path('update_profile/', update_profile),
    path('delete_profile/', delete_profile),
    
    # Board Urls
    path('create_board/', create_board),
    path('update_board/', update_board),
    path('delete_board/', delete_board),
    path('add_member_to_board/', add_member_to_board),
    path('remove_member_from_board/', remove_member_from_board),

    # Task Urls
    

]    