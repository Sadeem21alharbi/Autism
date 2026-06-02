from django.db import models
from django.conf import settings
from children.models import Child
from cloudinary.models import CloudinaryField


class SkillCategory(models.TextChoices):
    VISUAL   = 'visual',   'بصري'
    SENSORY  = 'sensory',  'حسي'
    MOTOR    = 'motor',    'حركي'
    LANGUAGE = 'language', 'لغوي'



class Activity(models.Model):

    LEVEL_CHOICES = [
        ('easy',   'سهل'),
        ('medium', 'متوسط'),
        ('hard',   'صعب'),
    ]

    title       = models.CharField(max_length=200, verbose_name="اسم النشاط")
    description = models.TextField(verbose_name="وصف النشاط")
    category = models.CharField(max_length=50,choices=SkillCategory.choices, verbose_name="التصنيف")
    level       = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='easy', verbose_name="المستوى")
    age_min     = models.PositiveIntegerField(default=2, verbose_name="العمر الأدنى")
    age_max     = models.PositiveIntegerField(default=12, verbose_name="العمر الأقصى")
    emoji       = models.CharField(max_length=10, blank=True, verbose_name="إيموجي")
    activity_file = models.CharField(max_length=100, blank=True, default='')
    is_active   = models.BooleanField(default=True, verbose_name="مفعّل")
    order       = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    duration_minutes = models.PositiveIntegerField(default=10,verbose_name="مدة النشاط بالدقائق")
    created_at  = models.DateTimeField(auto_now_add=True)
    tag         = models.CharField(max_length=50, blank=True)  


    class Meta:
        ordering = ['order']
        verbose_name = "نشاط"
        verbose_name_plural = "الأنشطة"

    def __str__(self):
        return f"{self.title} — {self.get_category_display()}"


class ResourceVideo(models.Model):

    title       = models.CharField(max_length=200, verbose_name="عنوا الفيديو")
    description = models.TextField(blank=True, verbose_name="وصف الفيديو")
    video_file  = CloudinaryField(resource_type='video', verbose_name="ملف الفيديو")
    thumbnail   = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True, verbose_name="صورة مصغرة")
    category = models.CharField(max_length=50,choices=SkillCategory.choices,verbose_name="التصنيف")
    age_min     = models.PositiveIntegerField(default=2, verbose_name="العمر الأدنى")
    age_max     = models.PositiveIntegerField(default=12, verbose_name="العمر الأقصى")
    is_active   = models.BooleanField(default=True, verbose_name="مفعّل")
    order       = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "فيديو تعليمي"
        verbose_name_plural = "الفيديوهات التعليمية"

    def __str__(self):
        return f"{self.title} — {self.get_category_display()}"
    


class VideoAnalysis(models.Model):

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="video_analyses"
    )

    video = models.TextField(verbose_name="رابط الفيديو")

    ai_summary = models.TextField()

    eye_contact_score = models.IntegerField()

    attention_score = models.IntegerField()

    repetitive_behavior_score = models.IntegerField()

    interaction_level_score = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.child.name} - Video Analysis"