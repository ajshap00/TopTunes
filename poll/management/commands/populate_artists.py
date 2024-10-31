from django.core.management.base import BaseCommand
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.utils.text import slugify
from poll.data import get_data, get_dominant_colors
from poll.models import Artist, Song, Album
import requests

class Command(BaseCommand):
    help = 'Populate artist data from Google Sheets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start_row',
            type=int,
            default=2,
            help='Row number to start fetching artist data from (default is 2).'
        )

    def handle(self, *args, **kwargs):
        start_row = kwargs['start_row']

        # Define the fields available for updating
        fields_to_update = {
            'name': 'Artist Name',
            'description': 'Description',
            'banner_color': 'Banner Color',
            'artist_img': 'Artist Image',
        }

        # Prompt user for fields to update
        print("Fields available for update:")
        for key, value in fields_to_update.items():
            print(f"- {value}")

        fields_input = input("Enter the fields you want to update (comma-separated, e.g., name, description, banner_color, artist_img) or press Enter to update all: ")

        # Determine which fields to update
        if fields_input:
            fields_to_update = set(field.strip() for field in fields_input.split(','))
        else:
            fields_to_update = set(fields_to_update.keys())  # Update all fields if none specified

        # Set the scope for Google Sheets access
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # Load your service account credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            r'C:/Users/Alex Shapiro/OneDrive/Desktop/VSCODE PROJECTS/TopTunes/poll/secret_key/secret_key.json',
            scope
        )

        # Authenticate with Google Sheets
        client = gspread.authorize(creds)

        # Open the Google Sheet
        spreadsheet = client.open("artist_data")
        worksheet = spreadsheet.sheet1

        # Fetch all existing artists at once
        existing_artists = {artist.slug: artist for artist in Artist.objects.all()}

        # Initialize counters
        artist_count = 0
        song_count = 0
        album_count = 0

        for cell in worksheet.range(f'A{start_row}:A100'):
            artist_name = cell.value.strip()
            if not artist_name:
                continue

            artist_slug = slugify(artist_name)

            # Check if the artist already exists
            artist = existing_artists.get(artist_slug)

            # Fetch artist data only if necessary
            artist_data = {}
            if 'artist_img' in fields_to_update or 'banner_color' in fields_to_update:
                try:
                    artist_data = get_data(artist_name)
                    if not artist_data:
                        self.stdout.write(self.style.WARNING(f"No data found for artist '{artist_name}'. Skipping..."))
                        continue
                except requests.exceptions.HTTPError as e:
                    self.stdout.write(self.style.ERROR(f"HTTP error occurred for artist '{artist_name}': {e}"))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error fetching data for artist '{artist_name}': {e}"))
                    continue

            # Prepare artist fields for creation or update
            artist_fields = {
                'name': artist_name,
                'slug': artist_slug,
                'description': artist_data.get('description', 'No description available') if 'description' in fields_to_update else None,
                'banner_color': artist_data.get('banner_color') if 'banner_color' in fields_to_update else None,
            }

            # Only fetch the artist image and extract the dominant color if it's in the fields_to_update
            if 'artist_img' in fields_to_update:
                artist_image_path = artist_data.get('artist_img')
                if artist_image_path:
                    try:
                        # Use the dominant color extraction from data.py
                        dominant_colors = get_dominant_colors(artist_image_path)
                        banner_color = dominant_colors[0] if dominant_colors.size > 0 else None
                        if banner_color is not None:
                            artist_fields['banner_color'] = '#{:02x}{:02x}{:02x}'.format(*banner_color)  # Convert to hex
                        else:
                            artist_fields['banner_color'] = None  # Set to None if no color found
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error extracting dominant color from image '{artist_image_path}': {e}"))
                        artist_fields['banner_color'] = None  # Set to None if extraction fails
                else:
                    artist_fields['banner_color'] = None

            # Create or update the artist
            if artist:
                # Update existing artist
                for field in fields_to_update:
                    if field in artist_fields and artist_fields[field] is not None:  # Only update specified fields
                        setattr(artist, field, artist_fields[field])
                        self.stdout.write(self.style.SUCCESS(f'Updated artist: {artist.name}, field: {field}, value: {artist_fields[field]}'))  # Log updated fields
                artist.save()  # Save the updated artist instance
            else:
                # Create new artist
                try:
                    artist = Artist.objects.create(**artist_fields)
                    self.stdout.write(self.style.SUCCESS(f'Created artist: {artist.name}'))
                    existing_artists[artist_slug] = artist  # Add new artist to existing artists
                    artist_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating artist '{artist_name}': {e}"))
                    continue  # Skip to the next artist

            # Prepare lists for bulk creation
            songs_to_create = []
            albums_to_create = []

            # Process songs
            for song in artist_data.get('topsongs', []):
                title = song.get('title')
                album_art = song.get('album_art')

                # Set the release date
                release_date = song.get('release_date', None)
                if release_date and len(release_date) == 4:  # If it's just a year, e.g., "2016"
                    release_date = f"{release_date}-01-01"  # Default to January 1st
                elif not release_date or len(release_date) != 10:
                    release_date = None  # Ensure release_date is None if invalid

                # Check if the song already exists
                if title and not Song.objects.filter(title=title, artist=artist).exists():
                    songs_to_create.append(
                        Song(
                            title=title,
                            release_date=release_date,
                            album_art=album_art,
                            artist=artist
                        )
                    )

            # Process albums
            for album in artist_data.get('albums', []):
                if isinstance(album, dict):  # Ensure we are dealing with a dictionary
                    title = album.get('title')
                    release_date = album.get('release_date')

                    # Set release_date to default to January 1st if just a year
                    if release_date and len(release_date) == 4:
                        release_date = f"{release_date}-01-01"

                    # Check if the album already exists
                    if title and not Album.objects.filter(title=title, artist=artist).exists():
                        albums_to_create.append(
                            Album(
                                title=title,
                                release_date=release_date,
                                album_art=album.get('album_art'),
                                artist=artist
                            )
                        )

            # Bulk create songs and albums if there are any to create
            if songs_to_create:
                Song.objects.bulk_create(songs_to_create)
                song_count += len(songs_to_create)

            if albums_to_create:
                Album.objects.bulk_create(albums_to_create)
                album_count += len(albums_to_create)

        self.stdout.write(self.style.SUCCESS('Successfully populated artist data'))
        self.stdout.write(self.style.SUCCESS(f'Total Artists: {artist_count}, Songs: {song_count}, Albums: {album_count}'))
