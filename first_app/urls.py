from django.urls import path

from . import views

urlpatterns = [
    path('chat/<int:conversation_id>/', views.chat_view, name='chat_view'),
    path('send_message/', views.send_message, name='send_message'),
    path('fetch_messages/<str:username>/', views.fetch_messages, name='fetch_messages'),
    path('redirect_to_conversation/', views.conversation_redirect, name='conversation_redirect'),
    path('create_conversation/', views.create_conversation, name= 'create_conversation'),
    path('register/', views.register_view, name = 'register'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
]
