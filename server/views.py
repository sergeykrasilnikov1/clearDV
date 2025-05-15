from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Video, CompanyLogo, Service, Application, Review, SectionContent
from .utils import send_telegram_message

# Create your views here.

def index(request):

    vl_rating = 4.9
    gis_rating = 4.9

    active_videos = Video.objects.filter(is_active=True).order_by('order')
    company_logos = CompanyLogo.objects.filter(is_active=True).order_by('order')
    services = Service.objects.filter(is_active=True).order_by('order')
    reviews = Review.objects.filter(is_active=True).order_by('-created_at')

    sections = {
        section.section: section 
        for section in SectionContent.objects.filter(is_active=True)
    }
    
    return render(request, 'index.html', {
        'active_videos': active_videos,
        'company_logos': company_logos,
        'services': services,
        'reviews': reviews,
        'vl_rating': vl_rating,
        'gis_rating': gis_rating,
        'sections': sections
    })

def submit_application(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            area = request.POST.get('area')
            question = request.POST.get('question')
            service_id = request.POST.get('service')

            service = Service.objects.get(id=service_id)

            application = Application.objects.create(
                name=name,
                phone=phone,
                area=area,
                question=question,
                service=service
            )
            telegram_message = f"""
<b>Новая заявка #{application.id}</b>

👤 <b>Имя:</b> {name}
📱 <b>Телефон:</b> {phone}
📐 <b>Площадь:</b> {area}
🔧 <b>Услуга:</b> {service.name}
❓ <b>Вопрос:</b> {question if question else 'Не указан'}
            """

            send_telegram_message(telegram_message)

            messages.success(request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect('index')

        except Service.DoesNotExist:
            messages.error(request, 'Выбранная услуга не найдена.')
        except Exception as e:
            messages.error(request, 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже.')

    return redirect('index')
