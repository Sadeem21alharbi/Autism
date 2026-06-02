from django.core.management.base import BaseCommand
from assessment.models import AssessmentQuestion


class Command(BaseCommand):
    help = 'تحشو أسئلة التقييم في قاعدة البيانات'

    def handle(self, *args, **kwargs):

        AssessmentQuestion.objects.all().delete()

        questions = [


            {'text': 'هل يتابع الطفل الأشياء المتحركة بعينيه؟', 'path': 'questionnaire', 'category': 'visual', 'source': 'M-CHAT البند 2', 'order': 1},
            {'text': 'هل يأتي لك بأشياء ليريك إياها؟', 'path': 'questionnaire', 'category': 'visual', 'source': 'M-CHAT البند 11', 'order': 2},
            {'text': 'هل يحافظ على التواصل البصري أثناء اللعب أو الحديث؟', 'path': 'questionnaire', 'category': 'visual', 'source': 'CARS-2 البند 3', 'order': 3},
            {'text': 'هل يشير بإصبعه نحو شيء يريده أو يثير اهتمامه؟', 'path': 'questionnaire', 'category': 'visual', 'source': 'M-CHAT البند 7', 'order': 4},

            {'text': 'هل يُغطي أذنيه عند سماع أصوات عادية؟', 'path': 'questionnaire', 'category': 'sensory', 'source': 'CARS-2 البند 6', 'order': 5},
            {'text': 'هل يرفض لمس بعض الأسطح أو الأقمشة؟', 'path': 'questionnaire', 'category': 'sensory', 'source': 'CARS-2 البند 6', 'order': 6},
            {'text': 'هل يبدو غير مبالٍ بالألم أحياناً؟', 'path': 'questionnaire', 'category': 'sensory', 'source': 'CARS-2 البند 7', 'order': 7},
            {'text': 'هل يشم الأشياء أو الأشخاص بشكل غير معتاد؟', 'path': 'questionnaire', 'category': 'sensory', 'source': 'CARS-2 البند 6', 'order': 8},

            {'text': 'هل يكرر حركات بيده أو جسمه باستمرار مثل الرفرفة أو التأرجح؟', 'path': 'questionnaire', 'category': 'motor', 'source': 'CARS-2 البند 5', 'order': 9},
            {'text': 'هل يمشي على أطراف أصابعه؟', 'path': 'questionnaire', 'category': 'motor', 'source': 'SCQ', 'order': 10},
            {'text': 'هل يصعب عليه الإمساك بالأشياء الصغيرة كالقلم؟', 'path': 'questionnaire', 'category': 'motor', 'source': 'CARS-2 البند 5', 'order': 11},
            {'text': 'هل يفقد توازنه أو يتعثر بشكل ملحوظ؟', 'path': 'questionnaire', 'category': 'motor', 'source': 'CARS-2 البند 5', 'order': 12},

            {'text': 'هل يستجيب لاسمه عند مناداته؟', 'path': 'questionnaire', 'category': 'language', 'source': 'M-CHAT البند 1', 'order': 13},
            {'text': 'هل يستطيع قول كلمتين متصلتين على الأقل؟', 'path': 'questionnaire', 'category': 'language', 'source': 'M-CHAT البند 5', 'order': 14},
            {'text': 'هل يكرر كلاماً سمعه دون فهم معناه (صدى الكلام)؟', 'path': 'questionnaire', 'category': 'language', 'source': 'SCQ', 'order': 15},
            {'text': 'هل يستخدم الإيماءات مثل التلويح والإشارة للتواصل؟', 'path': 'questionnaire', 'category': 'language', 'source': 'M-CHAT البند 10', 'order': 16},



            {'text': 'هل يصعب عليه تغيير الروتين اليومي دون انهيار عاطفي؟', 'path': 'video', 'category': 'sensory', 'source': 'CARS-2 البند 12', 'order': 1},
            {'text': 'هل لديه أطعمة يرفضها بشكل قاطع بسبب قوامها أو لونها؟', 'path': 'video', 'category': 'sensory', 'source': 'CARS-2 البند 12', 'order': 2},
            {'text': 'هل ينام بصعوبة أو يستيقظ كثيراً ليلاً؟', 'path': 'video', 'category': 'sensory', 'source': 'CARS-2 البند 12', 'order': 3},

            {'text': 'هل يبكي أو يصرخ دون سبب واضح تعرفه؟', 'path': 'video', 'category': 'language', 'source': 'CARS-2 البند 8', 'order': 4},
            {'text': 'هل لاحظت أنه لا يشعر بالألم كما يجب؟ مثلاً يقع ولا يبكي', 'path': 'video', 'category': 'sensory', 'source': 'CARS-2 البند 7', 'order': 5},
            {'text': 'هل يصعب تهدئته عند الانزعاج؟', 'path': 'video', 'category': 'language', 'source': 'CARS-2 البند 8', 'order': 6},

            {'text': 'هل يلعب بشكل خيالي؟ مثلاً يتظاهر بأن الموزة هاتف', 'path': 'video', 'category': 'visual', 'source': 'SCQ البند 8', 'order': 7},
            {'text': 'هل يفضل اللعب وحده دائماً بدلاً من الأطفال الآخرين؟', 'path': 'video', 'category': 'visual', 'source': 'SCQ البند 13', 'order': 8},
            {'text': 'هل يأتيك طلباً للمساعدة عند احتياجه لشيء؟', 'path': 'video', 'category': 'language', 'source': 'SCQ البند 13', 'order': 9},

            {'text': 'هل يتأثر بشدة من أماكن مزدحمة كالأسواق؟', 'path': 'video', 'category': 'sensory', 'source': 'CARS-2 البند 6', 'order': 10},
            {'text': 'هل يرفض ارتداء ملابس معينة بسبب إحساسها على جلده؟', 'path': 'video', 'category': 'sensory', 'source': 'CARS-2 البند 6', 'order': 11},
        ]

        for q in questions:
            AssessmentQuestion.objects.create(**q)

        self.stdout.write(self.style.SUCCESS(
            f'✅ تم إضافة {len(questions)} سؤال بنجاح'
        ))