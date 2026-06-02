import json
from openai import OpenAI
from django.conf import settings
from .models import Activity, ResourceVideo, SkillCategory

from decouple import config
client = OpenAI(api_key=config('OPENAI_API_KEY'))




def get_recommendations(video_analysis: str, questionnaire_answers: dict, child_age: int, child_info: dict = {}):

    prompt = f"""
    أنت متخصص في تقييم وتحليل سلوك أطفال التوحد.
    بناءً على المعلومات التالية، حدد التصنيفات التي يحتاج الطفل للدعم فيها.

    عمر الطفل: {child_age} سنوات
    نوع التواصل: {child_info.get('نوع التواصل', '')}
    الحساسية الحسية: {child_info.get('الحساسية الحسية', '')}
    الأهداف الحالية: {child_info.get('الأهداف الحالية', '')}
    ملاحظات ولي الأمر: {child_info.get('ملاحظات ولي الأمر', '')}

    نتيجة تحليل الفيديو:
    {video_analysis if video_analysis else "لا يوجد فيديو"}

    إجابات تقييم الأسئلة:
    {questionnaire_answers}

    التصنيفات المتاحة فقط (لا تستخدم غيرها):
    - visual:  صعوبات في التركيز البصري أو تتبع الأشياء بالعين
    - sensory: حساسية تجاه الأصوات أو اللمس أو الضوء أو الروائح
    - motor:   ضعف في المهارات الحركية الدقيقة أو الكبيرة
    - language: تأخر في الكلام أو التواصل اللغوي

    قواعد الرد:
    - رجّع فقط JSON array بالتصنيفات مرتبة من الأعلى أولوية للأقل
    - لا تضيف أي نص أو شرح خارج الـ JSON
    - مثال: ["sensory", "language", "visual"]
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    categories = json.loads(raw)

    valid_values     = [choice[0] for choice in SkillCategory.choices]
    valid_categories = [c for c in categories if c in valid_values]

    activities = Activity.objects.filter(
        category__in=valid_categories,
        age_min__lte=child_age,
        age_max__gte=child_age,
        is_active=True
    ).order_by('order')[:6]

    videos = ResourceVideo.objects.filter(
        category__in=valid_categories,
        age_min__lte=child_age,
        age_max__gte=child_age,
        is_active=True
    ).order_by('order')[:4]

    return {
        "categories": valid_categories,
        "activities": list(activities),
        "videos":     list(videos)
    }




def build_daily_routine(child_age: int, categories: list, child_info: dict = {}):

    prompt = f"""
    أنت متخصص في تأهيل أطفال طيف التوحد.
    بناءً على معلومات الطفل التالية، ابنِ له جدولاً يومياً روتينياً كاملاً ومناسباً.

    معلومات الطفل:
    - العمر: {child_age} سنوات
    - نوع التواصل: {child_info.get('نوع التواصل', '')}
    - الحساسية الحسية: {child_info.get('الحساسية الحسية', '')}
    - الأهداف الحالية: {child_info.get('الأهداف الحالية', '')}
    - ملاحظات ولي الأمر: {child_info.get('ملاحظات ولي الأمر', '')}
    - مجالات الدعم المطلوبة: {', '.join(categories)}

    الجدول اليومي يشمل هذه الفئات الثابتة:
    - روتين_صباح: الاستيقاظ والفطور
    - نشاط_صباح: نشاط تعليمي أو علاجي مخصص
    - غداء: وجبة الغداء ونصائح غذائية
    - قيلولة: وقت الراحة
    - نشاط_مساء: نشاط ثانٍ مخصص
    - عشاء: وجبة العشاء
    - روتين_نوم: التهيئة للنوم

    قواعد الرد — رجّع JSON فقط بهذا الشكل بدون أي نص خارجه:
    {{
        "routine": [
            {{
                "time": "8:00 ص",
                "title": "استيقاظ وفطور",
                "description": "وصف مخصص للطفل",
                "category": "روتين",
                "icon": "☀️",
                "tag": "روتين أساسي",
                "tag_color": "orange"
            }},
            {{
                "time": "10:00 ص",
                "title": "اسم النشاط",
                "description": "وصف مخصص بناءً على احتياجات الطفل",
                "category": "نشاط",
                "icon": "🖐️",
                "tag": "نشاط حسي",
                "tag_color": "purple"
            }}
        ],
        "behavioral_tip": "نصيحة سلوكية مخصصة للطفل",
        "calm_tip": "نصيحة تهدئة مخصصة للطفل"
    }}

    tag_color المتاحة: orange, purple, blue, green, yellow
    الجدول يحتوي على 7 عناصر بالضبط بالترتيب الزمني.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)