from django.core.management.base import BaseCommand
from poll.models import Artist, Song, Album
import poll

class Command(BaseCommand):
    help = 'Clears all artist data from the database'

    def handle(self, *args, **kwargs):
        # Deleting all songs, albums, and artists
        Song.objects.all().delete()
        Album.objects.all().delete()
        Artist.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully cleared all artist data.'))
