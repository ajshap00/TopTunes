from django.core.management.base import BaseCommand
from poll.models import Artist  # Adjust this import according to your project structure
from poll.data import get_data  # Ensure this import points to where your get_data function is defined

class Command(BaseCommand):
    help = 'Update artist descriptions if they are under 10 words'

    def handle(self, *args, **kwargs):
        # Fetch all artists
        artists = Artist.objects.all()

        for artist in artists:
            description_word_count = len(artist.description.split())

            if description_word_count < 10:
                # Fetch new data for the artist
                data = get_data(artist.name)

                if data and 'description' in data:
                    artist.description = data['description']  # Update the description
                    artist.save()  # Save the updated artist
                    self.stdout.write(self.style.SUCCESS(f'Updated description for artist: {artist.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No new description found for artist: {artist.name}'))
            else:
                # Use NOTICE for informational messages
                self.stdout.write(self.style.NOTICE(f'Artist {artist.name} has a sufficient description (words: {description_word_count})'))

        self.stdout.write(self.style.SUCCESS('Finished updating artist descriptions.'))

