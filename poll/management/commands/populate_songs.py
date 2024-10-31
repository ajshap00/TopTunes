from django.core.management.base import BaseCommand
from poll.models import Song
from poll.data import get_data

class Command(BaseCommand):
    help = 'Update preview URLs for all songs'

    def handle(self, *args, **kwargs):
        # Get all songs
        songs = Song.objects.all()

        for song in songs:
            # Fetch artist data based on the song title
            data = get_artist_data(song.title)  # Modify if needed to get artist-specific data

            if data and 'topsongs' in data:
                # Find the track that matches the song title in the top songs
                for track in data['topsongs']:
                    if track['title'].lower() == song.title.lower():
                        # Check if 'preview_url' exists in the track data
                        if 'preview_url' in track:
                            song.preview = track['preview_url']  # Update the preview URL
                            song.save()  # Save the updated song
                            self.stdout.write(self.style.SUCCESS(f'Updated preview for song: {song.title}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'No preview found for song: {song.title}'))
                        break
                else:
                    self.stdout.write(self.style.WARNING(f'No matching track found for song: {song.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'No data found for song: {song.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated all song previews'))
