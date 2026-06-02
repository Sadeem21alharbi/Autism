from django.shortcuts import render, redirect
from .forms import SubscriberForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string

def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            
            
            html_content = render_to_string('notifications/email_welcome.html', {'email': email})
            
            
            try:
                send_mail(
                    'مرحباً بك في إحتواء',
                    'شكراً لاشتراكك في موقعنا',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                    html_message=html_content
                )
            except Exception as e:
                print(f"Error sending email: {e}")
            
            messages.success(request, "تم الاشتراك بنجاح!")
        else:
            messages.error(request, "هذا البريد الإلكتروني مسجل بالفعل أو غير صالح.")
            
        return redirect(request.META.get('HTTP_REFERER', '/'))
        
    return redirect('/')
