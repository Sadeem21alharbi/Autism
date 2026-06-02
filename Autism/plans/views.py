from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpRequest, HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.staticfiles import finders
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from children.models import Child
from plans.models import SupportPlan,PlanActivity
from ai_analysis.models import VideoAnalysis,Activity,ResourceVideo
from openai import OpenAI
from assessment.models import AssessmentSession,AssessmentAnswer
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import json
import os
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse
from django.conf import settings
import matplotlib.pyplot as plt
import io
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

def ar(text):
    return get_display(reshape(str(text)))


def support_plan_redirect(request):
    plan = SupportPlan.objects.filter(user=request.user).first()

    if not plan:
        return redirect(f"{reverse('main:home_page_view')}#start")

    return redirect('plans:main_plan_view')



@login_required(login_url='accounts:signin')
def support_plan_view(request: HttpRequest):

    plan = SupportPlan.objects.filter(user=request.user).first()

    if not plan:
        categories         = request.session.get('result_categories', [])
        activity_ids       = request.session.get('result_activities', [])
        ai_summary         = request.session.get('ai_summary', '')
        daily_routine_data = request.session.get('daily_routine', {})

        if not categories:
            return redirect('assessment:questionnaire')

        session = AssessmentSession.objects.filter(
            user=request.user,
            status='completed'
        ).first()

        if not session:
            return redirect('assessment:questionnaire')

        child_age = (date.today() - session.child.birth_date).days // 365

        
        selected_activities = []
        for cat in categories[:2]:
            activity = Activity.objects.filter(
                category=cat,
                age_min__lte=child_age,
                age_max__gte=child_age,
                is_active=True
            ).order_by('order').first()
            if activity:
                selected_activities.append(activity)

        
        if len(selected_activities) < 2:
            extra = list(Activity.objects.filter(id__in=activity_ids))
            for act in extra:
                if act not in selected_activities:
                    selected_activities.append(act)
                if len(selected_activities) >= 2:
                    break

        
        days = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
        weekly_activities = []

        for i, day in enumerate(days):
            act1 = selected_activities[(i * 2) % len(selected_activities)] if selected_activities else None
            act2 = selected_activities[(i * 2 + 1) % len(selected_activities)] if len(selected_activities) > 1 else None

            if act1:
                weekly_activities.append({
                    'day':         day,
                    'activity':    act1.title,
                    'description': act1.description,
                    'category':    act1.category,
                    'duration':    act1.duration_minutes,
                    'activity_id': act1.id,
                })
            if act2:
                weekly_activities.append({
                    'day':         day,
                    'activity':    act2.title,
                    'description': act2.description,
                    'category':    act2.category,
                    'duration':    act2.duration_minutes,
                    'activity_id': act2.id,
                })

        weekly_plan = {
            'routine':         daily_routine_data.get('routine', []),
            'calm_tip':        daily_routine_data.get('calm_tip', ''),
            'behavioral_tip':  daily_routine_data.get('behavioral_tip', ''),
            'activities':      weekly_activities,
        }

        plan = SupportPlan.objects.create(
            session=session,
            child=session.child,
            user=request.user,
            categories=categories,
            ai_summary=ai_summary,
            weekly_plan=weekly_plan,
        )

        for item in weekly_activities:
            PlanActivity.objects.create(
                plan=plan,
                day=item['day'],
                title=item['activity'],
                description=item['description'],
                category=item['category'],
                duration_minutes=item['duration'],
                activity_id=item['activity_id'],
            )

        for key in ['result_categories', 'result_activities', 'result_videos', 'ai_summary', 'daily_routine']:
            request.session.pop(key, None)

    plan_activities  = PlanActivity.objects.filter(plan=plan)
    current_activity = plan_activities.first()
    next_activity    = plan_activities[1] if plan_activities.count() > 1 else None

    child_age = (date.today() - plan.child.birth_date).days // 365
    videos = ResourceVideo.objects.filter(
        category__in=plan.categories,
        age_min__lte=child_age,
        age_max__gte=child_age,
        is_active=True
    ).order_by('order')[:4]

    start_date = plan.created_at
    end_date   = start_date + timezone.timedelta(days=6)

    return render(request, 'plans/support_plan.html', {
        'plan':             plan,
        'current_activity': current_activity,
        'next_activity':    next_activity,
        'plan_activities':  plan_activities,
        'videos':           videos,
        'categories':       plan.categories,
        'ai_summary':       plan.ai_summary,
        'start_date':       start_date.strftime('%d %B'),
        'end_date':         end_date.strftime('%d %B'),
        'child':            plan.child,
    })



@login_required(login_url='accounts:signin')
def main_plan_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()

    if not plan:
        return redirect('assessment:questionnaire')

    today     = date.today()
    day_names = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']

    week_days = []
    for i in range(5):
        d = today + timedelta(days=i - 2)
        week_days.append({
            'name':     day_names[d.weekday()],
            'date':     d.strftime('%d %B'),
            'is_today': d == today,
        })

    other_days = [d for d in week_days if not d['is_today']][2:]

    daily_routine    = []
    calm_tip         = ''
    behavioral_tip   = ''
    current_activity = None
    next_activity    = None
    today_activities = []

    day_map = {
        'الاثنين': 'monday', 'الثلاثاء': 'tuesday',
        'الأربعاء': 'wednesday', 'الخميس': 'thursday',
        'الجمعة': 'friday', 'السبت': 'saturday', 'الأحد': 'sunday'
    }
    today_key        = day_map.get(day_names[today.weekday()], '')
    today_activities = PlanActivity.objects.filter(plan=plan, day=today_key)
    current_activity = today_activities.first()
    next_activity    = today_activities[1] if today_activities.count() > 1 else None

    stored = plan.weekly_plan
    if isinstance(stored, dict):
        daily_routine  = stored.get('routine', [])
        calm_tip       = stored.get('calm_tip', '')
        behavioral_tip = stored.get('behavioral_tip', '')

    return render(request, 'plans/main_plan.html', {
        'plan':             plan,
        'week_days':        week_days,
        'other_days':       other_days,
        'today_activities': today_activities,
        'current_activity': current_activity,
        'next_activity':    next_activity,
        'today_display':    f"{day_names[today.weekday()]} {today.strftime('%d %B')}",
        'daily_routine':    daily_routine,
        'calm_tip':         calm_tip,
        'behavioral_tip':   behavioral_tip,
    })




@login_required(login_url='accounts:signin')
def video_plan_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()
    if not plan:
        return redirect(f"{reverse('main:home_page_view')}#start")

    videos = []
    if plan:
        child_age = (date.today() - plan.child.birth_date).days // 365
        videos = ResourceVideo.objects.filter(
            category__in=plan.categories,
            age_min__lte=child_age,
            age_max__gte=child_age,
            is_active=True
        ).order_by('order')[:6]

    return render(request, 'plans/video_plan.html', {
        'videos': videos,
        'plan':   plan,
    })




@login_required(login_url='accounts:signin')
def support_strategies_view(request: HttpRequest):
    plan = SupportPlan.objects.filter(user=request.user).first()

    strategies = []
    if plan:
        category_strategies = {
            'visual': [
                'استخدم بطاقات مصورة ملونة أثناء الحديث مع طفلك',
                'قلل من المشتتات البصرية في غرفة الدراسة',
                'استخدم الإشارات البصرية بدلاً من التعليمات اللفظية فقط',
            ],
            'sensory': [
                'وفر بيئة هادئة وخالية من الضوضاء قدر الإمكان',
                'استخدم سماعات عند وجود أصوات مزعجة',
                'جرب الأقمشة الناعمة في ملابس طفلك',
            ],
            'motor': [
                'خصص وقتاً يومياً للعب الحر والحركة',
                'استخدم أدوات مساعدة للكتابة إذا لزم',
                'جرب تمارين التوازن البسيطة مع طفلك',
            ],
            'language': [
                'تحدث مع طفلك ببطء ووضوح',
                'كرر الكلمات الجديدة في سياقات مختلفة',
                'استخدم الغناء والأناشيد لتطوير اللغة',
            ],
        }

        for cat in plan.categories:
            if cat in category_strategies:
                strategies.extend(category_strategies[cat])
        strategies = strategies[:3]

    return render(request, 'plans/support_strategies.html', {
        'strategies': strategies,
        'plan':       plan,
    })




@login_required(login_url='accounts:signin')
def update_plan_feedback(request):
    if request.method != "POST":
        return JsonResponse({'success': False})

    try:
        data     = json.loads(request.body)
        feedback = data.get('feedback', '').strip()
        plan     = SupportPlan.objects.filter(user=request.user).first()

        if not plan or not feedback:
            return JsonResponse({'success': False, 'error': 'بيانات غير كاملة'})

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""
        أنت متخصص في دعم أطفال طيف التوحد.
        ولي الأمر أرسل هذه الملاحظة عن طفله بعد تجربة الخطة:

        "{feedback}"

        معلومات الطفل:
        - التصنيفات الحالية: {', '.join(plan.categories)}
        - ملخص الخطة: {plan.ai_summary}

        بناءً على هذه الملاحظة:
        1. حدد المشكلة الرئيسية التي يواجهها الطفل
        2. اقترح تعديلاً محدداً على الخطة أو نشاطاً بديلاً مناسباً
        3. أعطِ نصيحة عملية لولي الأمر يطبقها مباشرة

        الرد يكون:
        - باللغة العربية
        - موجز وواضح وعملي
        - بدون ترقيم أو عناوين
        - لا يتجاوز 3 جمل
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        suggestion = response.choices[0].message.content.strip()

        return JsonResponse({'success': True, 'suggestion': suggestion})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

   



import os
import io
import matplotlib.pyplot as plt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
