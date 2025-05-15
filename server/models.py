from django.db import models
import os
from django.conf import settings
import yt_dlp
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def convert_to_webp(image_field):
    if not image_field:
        return

    img = Image.open(image_field)

    img_io = BytesIO()

    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')

    img.save(img_io, 'WEBP', quality=85, optimize=True)

    new_name = os.path.splitext(image_field.name)[0] + '.webp'

    img_io.seek(0)
    return ContentFile(img_io.getvalue(), name=new_name)

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=200)
    youtube_url = models.URLField()
    video_file = models.FileField(upload_to='videos/')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', '-created_at']

    def download_video(self):
        videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        os.makedirs(videos_dir, exist_ok=True)

        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(videos_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'nocheckcertificate': True,
            'no_warnings': False,
            'socket_timeout': 30,
            'retries': 10,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.youtube_url, download=True)
                filename = ydl.prepare_filename(info)
                self.title = info.get('title', self.title)
                self.video_file = os.path.join('videos', os.path.basename(filename))
        except Exception as e:
            raise Exception(f"Ошибка при скачивании видео: {str(e)}. Попробуйте обновить yt-dlp командой 'pip install -U yt-dlp'")

    def delete_video_file(self):
        if self.video_file:
            try:
                full_path = os.path.join(settings.MEDIA_ROOT, self.video_file.name)
                if os.path.exists(full_path):
                    os.remove(full_path)
            except Exception:
                pass

    def save(self, *args, **kwargs):
        if self.pk:
            old_video = Video.objects.get(pk=self.pk)
            if old_video.youtube_url != self.youtube_url:
                self.delete_video_file()
                try:
                    self.download_video()
                except Exception as e:
                    self.youtube_url = old_video.youtube_url
                    raise Exception(f"Ошибка при скачивании видео: {str(e)}")
        else:
            try:
                self.download_video()
            except Exception as e:
                raise Exception(f"Ошибка при скачивании видео: {str(e)}")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.delete_video_file()
        super().delete(*args, **kwargs)

class CompanyLogo(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название компании')
    logo = models.ImageField(upload_to='logos/', verbose_name='Логотип')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    order = models.IntegerField(default=0, verbose_name='Порядок отображения')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.logo:
            webp_image = convert_to_webp(self.logo)
            if webp_image:
                self.logo = webp_image
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order',]
        verbose_name = 'Логотип компании'
        verbose_name_plural = 'Логотипы компаний'

class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название услуги')
    description = models.TextField(verbose_name='Описание')
    duration = models.CharField(max_length=50, verbose_name='Время выполнения')
    area = models.CharField(max_length=50, verbose_name='Площадь в м²')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    photo = models.ImageField(upload_to='services/', verbose_name='Фото услуги')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    order = models.IntegerField(default=0, verbose_name='Порядок отображения')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.photo:
            webp_image = convert_to_webp(self.photo)
            if webp_image:
                self.photo = webp_image
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

class Application(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя клиента')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    area = models.CharField(max_length=50, verbose_name='Площадь')
    question = models.TextField(blank=True, null=True, verbose_name='Вопрос')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"{self.name} - {self.service.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

class Review(models.Model):
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]
    external_id = models.CharField(max_length=50, unique=True, verbose_name='Внешний ID')
    link = models.URLField(verbose_name='Ссылка на отзыв')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга', null=True, blank=True)
    text = models.TextField(verbose_name='Текст отзыва')
    name = models.CharField(max_length=200, verbose_name='Имя автора')
    photo = models.ImageField(upload_to='reviews/', verbose_name='Фото автора')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    def __str__(self):
        service_name = self.service.name if self.service else "Общий отзыв"
        return f"{self.name} - {service_name} - {self.rating}★"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

class SectionContent(models.Model):
    SECTION_CHOICES = [
        ('hero', 'Главный экран'),
        ('about', 'О нас'),
        ('services', 'Услуги'),
        ('portfolio', 'Портфолио'),
        ('reviews', 'Отзывы'),
        ('clients', 'Клиенты'),
        ('contact', 'Контакты'),
    ]

    section = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES,
        unique=True,
        verbose_name='Секция'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        blank=True
    )
    subtitle = models.CharField(
        max_length=200,
        verbose_name='Подзаголовок',
        blank=True
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Отображать секцию'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"

    class Meta:
        verbose_name = 'Содержимое секции'
        verbose_name_plural = 'Содержимое секций'
        ordering = ['section']
