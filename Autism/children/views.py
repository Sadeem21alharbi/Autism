from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Child
from datetime import date
from django.contrib import messages
from assessment.models import AssessmentSession,AssessmentAnswer
from plans.models import SupportPlan, PlanActivity


@login_required
def profile_view(request, id):
    child = get_object_or_404(Child, id=id, user=request.user)

    age = None
    if child.birth_date:
        today = date.today()
        age = today.year - child.birth_date.year
        if (today.month, today.day) < (child.birth_date.month, child.birth_date.day):
            age -= 1

    sessions_count = AssessmentSession.objects.filter(child=child).count()
    plan           = SupportPlan.objects.filter(child=child).first()
    skills_count   = len(plan.categories) if plan else 0
    activities_count = PlanActivity.objects.filter(plan=plan).count() if plan else 0

    skill_progress = []
    if plan:
        category_names = {
            'visual':   'التواصل البصري',
            'sensory':  'الحساسية الحسية',
            'motor':    'المهارات الحركية',
            'language': 'التواصل اللغوي',
        }
        for cat in plan.categories[:3]:
            skill_progress.append({
                'name':  category_names.get(cat, cat),
                'level': 'في التطور',
                'pct':   50,
            })

    last_sessions = AssessmentSession.objects.filter(
        child=child
    ).order_by('-created_at')[:3]

    return render(request, 'children/profile.html', {
        'child':            child,
        'age':              age,
        'sessions_count':   sessions_count,
        'skills_count':     skills_count,
        'activities_count': activities_count,
        'skill_progress':   skill_progress,
        'last_sessions':    last_sessions,
    })

@login_required
def edit_child(request, id):
    child = get_object_or_404(Child, id=id, user=request.user)

    if request.method == "POST" and request.POST.get("delete_child") == "1":
        child.delete()
        return redirect("main:home_page_view")  
    
    if request.method == 'POST':
        child.name = request.POST.get('name')
        child.birth_date = request.POST.get('age')
        child.gender = request.POST.get('gender')
        child.communication_type = request.POST.get('communication_type')
        child.sensory_sensitivities = request.POST.get('sensory_sensitivities')
        child.goals = request.POST.get('goals')
        child.notes = request.POST.get('notes')

        child.save()
        messages.success(request, "تم حفظ التعديلات بنجاح")

        return redirect('children:profile', id=child.id)

    return render(request, 'children/edit-profile.html', {
        'child': child
    })


@login_required
def add_child_view(request):
    if request.method == "POST":
        child = Child.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            birth_date = request.POST.get('age'),
            gender=request.POST.get("gender"),
            communication_type=request.POST.get("communication_type"),
            sensory_sensitivities=request.POST.get("sensory_sensitivities"),
            goals=request.POST.get("goals"),
            notes=request.POST.get("notes"),
        )
        
        messages.success(request,"تم اضافة الطفل بنجاح")


        return redirect('children:profile', id=child.id)

    return render(request, 'children/add-child.html')


@login_required
def delete_child(request, id):
    child = Child.objects.get(id=id, user=request.user)

    if request.method == "POST":
        child.delete()
        messages.success(request, "تم حذف ملف الطفل بنجاح")
        return redirect("main:home_page_view")  

    return redirect("children:profile", id=id)