from django.core.management.base import BaseCommand
from server.models import Video
import os
from django.conf import settings
import yt_dlp

# Список видео для загрузки
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=qtPBWpo7fnI",
    "https://www.youtube.com/watch?v=aZfQF2LL6Xo",
    "https://www.youtube.com/watch?v=PZIcR7VHi-U"
]

class Command(BaseCommand):
    help = 'Downloads YouTube videos and saves them to the database'

    def add_arguments(self, parser):
        parser.add_argument('youtube_urls', nargs='*', type=str, help='YouTube video URLs')
        parser.add_argument('--delete-old', action='store_true', help='Delete old videos')
        parser.add_argument('--use-list', action='store_true', help='Use predefined list of videos')

    def handle(self, *args, **options):
        youtube_urls = options['youtube_urls']
        delete_old = options['delete_old']
        use_list = options['use_list']

        # Если указан флаг --use-list или не переданы URL, используем список из VIDEO_URLS
        if use_list or not youtube_urls:
            youtube_urls = VIDEO_URLS

        try:
            videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
            os.makedirs(videos_dir, exist_ok=True)

            if delete_old:
                old_videos = Video.objects.all()
                for video in old_videos:
                    if video.video_file:
                        try:
                            os.remove(os.path.join(settings.MEDIA_ROOT, video.video_file.name))
                        except:
                            pass
                    video.delete()
                self.stdout.write(self.style.SUCCESS('Old videos deleted'))

            for index, youtube_url in enumerate(youtube_urls):
                ydl_opts = {
                    'format': 'best[ext=mp4]',
                    'outtmpl': os.path.join(videos_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=True)
                    filename = ydl.prepare_filename(info)

                video_obj = Video.objects.create(
                    title=info.get('title', f'Video {index + 1}'),
                    youtube_url=youtube_url,
                    video_file=os.path.join('videos', os.path.basename(filename)),
                    order=index
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully downloaded video: {video_obj.title}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error downloading videos: {str(e)}'))