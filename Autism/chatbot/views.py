from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Conversation, ChatMessage
from .serializers import ChatMessageSerializer



def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')

def chatbot_history(request):
    return render(request, 'chatbot/chatbot_history.html')

def chatbot_window(request):
    return render(request, 'chatbot/chatbot_window.html')



def get_or_create_conversation(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)
    
    conv, _ = Conversation.objects.get_or_create(user=request.user)
    return JsonResponse({"conv_id": conv.id})



@api_view(['POST'])
def create_conversation(request):
    if not request.user.is_authenticated:
        return Response({"error": "login required"}, status=401)

    conv = Conversation.objects.create(user=request.user)
    return Response({"id": conv.id})



@api_view(['POST'])
def send_message(request, conv_id):
    content = request.data.get('content')

    if not content:
        return Response({"error": "content is required"}, status=400)

    try:
        conv = Conversation.objects.get(id=conv_id)
    except Conversation.DoesNotExist:
        raise Http404("Conversation not found")

    
    msg = ChatMessage.objects.create(
        conversation=conv,
        message_type='user',
        content=content
    )

    
    ai_content = ""
    try:
        from decouple import config
        import google.generativeai as genai
        
        gemini_api_key = config('GEMINI_API_KEY', default='')
        openai_api_key = config('OPENAI_API_KEY', default='')
        
        system_prompt = (
                    "أنت مساعد ذكي يساعد أولياء الأمور على فهم سلوكيات أطفالهم "
                    "وتقديم معلومات مبسطة وداعمة حول اضطراب طيف التوحد."

                    "يجب الالتزام بالتالي: "

                    "1. لا تقم بتشخيص الطفل بشكل مؤكد. "
                    "2. اشرح العلامات والسلوكيات والأسباب المحتملة بطريقة بسيطة وواضحة. "
                    "3. قدم نصائح عملية لدعم الطفل في الحياة اليومية. "
                    "4. استخدم أسلوبًا ودودًا ومطمئنًا ومناسبًا لولي الأمر. "
                    "5. تجنب الردود القصيرة أو العامة جدًا. "
                    "6. لا تكرر عبارات مثل: أنا هنا للمساعدة في كل رد. "
                    "7. إذا سأل المستخدم عن سبب سلوك معين، قدم تفسيرًا مبسطًا واحتمالات ممكنة دون تشخيص قاطع."
                )

        recent_messages = ChatMessage.objects.filter(conversation=conv).order_by('created_at')[:20]

        
        generated = False

        

        
        if not generated and openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_api_key)
                
                messages_for_ai = [
                    {"role": "system", "content": system_prompt}
                ]
                for m in recent_messages:
                    role = 'user' if m.message_type == 'user' else 'assistant'
                    messages_for_ai.append({"role": role, "content": m.content})
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_ai,
                    temperature=0.7,
                    max_tokens=300,
                    presence_penalty=0.3,
                )
                print(response)
                ai_content = response.choices[0].message.content
                print(ai_content)
                generated = True
            except Exception as e_openai:
                print("OPENAI ERROR:", e_openai)

                ai_content = f"حدث خطأ أثناء التواصل مع الذكاء الاصطناعي (OpenAI): {str(e_openai)}"
        
        
        if not generated:
            if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
                if not openai_api_key:
                    ai_content = "عذراً، لم يتم إعداد مفاتيح API الخاصة بـ Gemini أو OpenAI. يرجى إضافة المفاتيح اللازمة إلى ملف .env."
                else:
                    ai_content = "عذراً، حدث خطأ أثناء محاولة الاتصال بـ Gemini، وجاري استخدام OpenAI كبديل ولكن يبدو أن هناك مشكلة."
            else:
                ai_content = "عذراً، فشل كلا النموذجين (Gemini و OpenAI) في الاستجابة. يرجى التحقق من صحة مفاتيح الـ API أو حالة الاتصال بالإنترنت."

    except Exception as e:
        ai_content = f"حدث خطأ غير متوقع: {str(e)}"

    
    ai_msg = ChatMessage.objects.create(
        conversation=conv,
        message_type='ai',
        content=ai_content
    )

    return Response({
    "user_message": ChatMessageSerializer(msg).data,
    "ai_message": ChatMessageSerializer(ai_msg).data
})



@api_view(['GET'])
def get_messages(request, conv_id):
    messages = ChatMessage.objects.filter(
        conversation_id=conv_id
    ).order_by('created_at')

    return Response(ChatMessageSerializer(messages, many=True).data)