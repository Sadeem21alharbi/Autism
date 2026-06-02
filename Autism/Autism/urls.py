"""
URL configuration for Autism project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('community/', include('community.urls')),
    path('children/', include('children.urls')),
    path('', include('plans.urls')), 
    path('', include('educational_videos.urls')),
    path('assessment/', include ('assessment.urls')),
    path('activities/', include('activity.urls', namespace='activity')), 
    path('',include('support_map.urls')),
    path('reset-password/',auth_views.PasswordResetView.as_view(template_name='accounts/reset-password.html'),name='password_reset'),
    path('reset-password/done/',auth_views.PasswordResetDoneView.as_view(template_name='accounts/reset-password-done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='accounts/reset-password-confirm.html'),name='password_reset_confirm'),
    path('reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='accounts/reset-password-complete.html'),name='password_reset_complete'),
    path('notifications/', include('notifications.urls')),
    path('chatbot/', include ('chatbot.urls')),
    path('payments/', include('payments.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]
