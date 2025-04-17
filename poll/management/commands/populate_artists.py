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

        field_names = {
            'name': 'Artist Name',
            'description': 'Description',
            'banner_color': 'Banner Color',
            'artist_img': 'Artist Image',
        }

        print("Fields available for update:")
        for key, value in field_names.items():
            print(f"- {value}")

        fields_input = input("Enter the fields you want to update (comma-separated, e.g., name, description, banner_color, artist_img) or press Enter to update all: ")

        fields_to_update = set(field.strip() for field in fields_input.split(',')) if fields_input else set(field_names.keys())

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            r'C:/Users/Alex Shapiro/OneDrive/Desktop/VSCODE PROJECTS/TopTunes/poll/secret_key/secret_key.json',
            scope
        )

        client = gspread.authorize(creds)
        worksheet = client.open("artist_data").sheet1

        artist_count = 0
        song_count = 0
        album_count = 0

        for cell in worksheet.range(f'A{start_row}:A100'):
            artist_name = cell.value.strip()
            if not artist_name:
                continue

            artist_slug = slugify(artist_name)
            artist = Artist.objects.filter(slug=artist_slug).first()

            try:
                artist_data = get_data(artist_name)
                if not artist_data:
                    self.stdout.write(self.style.WARNING(f"No data found for artist '{artist_name}'. Skipping..."))
                    continue
            except requests.exceptions.HTTPError as e:
                self.stdout.write(self.style.ERROR(f"HTTP error for artist '{artist_name}': {e}"))
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching data for artist '{artist_name}': {e}"))
                continue

            artist_fields = {
                'name': artist_name,
                'slug': artist_slug,
                'description': artist_data.get('description', 'No description available') if 'description' in fields_to_update else None,
                'banner_color': artist_data.get('banner_color') if 'banner_color' in fields_to_update else None,
            }

            if 'artist_img' in fields_to_update:
                artist_image_path = artist_data.get('artist_img')
                if artist_image_path:
                    try:
                        dominant_colors = get_dominant_colors(artist_image_path)
                        banner_color = dominant_colors[0] if dominant_colors.size > 0 else None
                        artist_fields['banner_color'] = '#{:02x}{:02x}{:02x}'.format(*banner_color) if banner_color else None
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error extracting color from '{artist_image_path}': {e}"))
                        artist_fields['banner_color'] = None
                else:
                    artist_fields['banner_color'] = None

            artist, created = Artist.objects.get_or_create(slug=artist_slug, defaults=artist_fields)

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created new artist: {artist.name}, banner_color: {artist_fields.get("banner_color")}'
                ))
                artist_count += 1
            else:
                updated = False
                for field in fields_to_update:
                    value = artist_fields.get(field)
                    current_value = getattr(artist, field, None)
                    if value and (not current_value or current_value in ['', 'No description available']):
                        setattr(artist, field, value)
                        updated = True
                        self.stdout.write(self.style.SUCCESS(
                            f'Updated artist: {artist.name}, field: {field}, value: {value}'
                        ))

                if updated:
                    artist.save()
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Artist '{artist.name}' already exists with sufficient data. Skipping update."
                    ))

            songs_to_create = []
            for song in artist_data.get('topsongs', []):
                title = song.get('title')
                album_art = song.get('album_art')
                release_date = song.get('release_date', None)

                if release_date and len(release_date) == 4:
                    release_date = f"{release_date}-01-01"
                elif not release_date or len(release_date) != 10:
                    release_date = None

                if title and not Song.objects.filter(title=title, artist=artist).exists():
                    songs_to_create.append(
                        Song(
                            title=title,
                            release_date=release_date,
                            album_art=album_art,
                            artist=artist
                        )
                    )

            albums_to_create = []
            for album in artist_data.get('albums', []):
                if isinstance(album, dict):
                    title = album.get('title', '')[:100]
                    release_date = album.get('release_date')
                    if release_date and len(release_date) == 4:
                        release_date = f"{release_date}-01-01"

                    if title and not Album.objects.filter(title=title, artist=artist).exists():
                        albums_to_create.append(
                            Album(
                                title=title,
                                release_date=release_date,
                                album_art=album.get('album_art'),
                                artist=artist
                            )
                        )

            if songs_to_create:
                Song.objects.bulk_create(songs_to_create)
                song_count += len(songs_to_create)

            if albums_to_create:
                Album.objects.bulk_create(albums_to_create)
                album_count += len(albums_to_create)

        self.stdout.write(self.style.SUCCESS('✅ Done populating artist data'))
        self.stdout.write(self.style.SUCCESS(f'Total Artists Created: {artist_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total Songs: {song_count}, Albums: {album_count}'))
