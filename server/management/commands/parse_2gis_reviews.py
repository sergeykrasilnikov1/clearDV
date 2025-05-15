from django.core.management.base import BaseCommand
from django.conf import settings
from server.models import Review
import requests
import json
from datetime import datetime
import time

class Command(BaseCommand):
    help = 'Парсит отзывы с 2ГИС'

    def add_arguments(self, parser):
        parser.add_argument('--org-id', type=str, help='ID организации в 2ГИС')
        parser.add_argument('--city', type=str, help='Город в 2ГИС')

    def handle(self, *args, **options):
        org_id = options['org_id'] or settings.GIS_ORG_ID
        city = options['city'] or settings.GIS_CITY

        if not org_id or not city:
            self.stdout.write(self.style.ERROR('Необходимо указать org_id и city'))
            return

        url = f"https://public-api.reviews.2gis.com/2.0/orgs/70000001061578973/reviews?limit=50&fields=meta.org_rating&key=6e7e1929-4ea9-4a5d-8c05-d601860389bd&locale=ru_RU"
        params = {
            "key": settings.GIS_API_KEY,
            # "page": 1,
            # "page_size": 100,
            "fields": "items.review_id,items.rating,items.text,items.author,items.date,items.answer"
        }

        try:
            self.stdout.write(f"Отправляем запрос к API 2ГИС: {url}")
            self.stdout.write(f"Параметры запроса: {params}")
            
            response = requests.get(url)
            self.stdout.write(f"Статус ответа: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()

            if 'reviews' in data:
                reviews = data['reviews']
                self.stdout.write(f"Найдено отзывов: {len(reviews)}")
                
                for review_data in reviews:
                    external_id = review_data['id']
                    if not Review.objects.filter(external_id=external_id).exists():

                        # date_created = parse_datetime(review_data['date_created'])

                        review = Review.objects.create(
                            external_id=external_id,
                            name=review_data['user']['name'],
                            text=review_data['text'],
                            rating=review_data['rating'],
                            # platform='2gis',
                            is_active=True,
                            link=f"https://2gis.ru/vladivostok/firm/{org_id}/tab/reviews/review/{external_id}"
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Добавлен отзыв от {review_data["user"]["name"]}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Отзыв {external_id} уже существует')
                        )

                if 'meta' in data and 'next_link' in data['meta']:
                    self.stdout.write("Обнаружены дополнительные страницы отзывов")
                self.stdout.write(self.style.SUCCESS('Парсинг отзывов завершен'))
            else:
                self.stdout.write(self.style.ERROR('Не удалось получить отзывы'))
                self.stdout.write(f"Полученный ответ: {data}")

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при запросе к API 2ГИС: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {e}'))