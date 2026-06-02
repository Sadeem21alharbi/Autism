
from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path('chatwindow/', views.chatbot_view, name='chatbot_view'),
    path('history/', views.chatbot_history, name='chatbot_history'),
    path('chatbotwindow/', views.chatbot_window, name='chatbot_window'),
    path('conversation/create/', views.create_conversation),
    path('conversation/<int:conv_id>/send/', views.send_message),
    path('conversation/<int:conv_id>/messages/', views.get_messages),
    path('get-conversation/', views.get_or_create_conversation),  
]