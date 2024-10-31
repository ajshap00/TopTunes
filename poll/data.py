import spotipy
from spotipy import SpotifyException
import time
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup
import re
from more_itertools import chunked
from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from io import BytesIO
import colorsys
from Goat import settings

CLIENT_ID = settings.SPOTIFY_CLIENT_ID
CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET

def get_spotify_client():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

sp = get_spotify_client()

def get_data(artist_name):
    from poll.models import Artist
    # Get the artist's Spotify ID
    artist_id = get_artist_id(sp, artist_name)

    # Fetch artist image URL
    artist_image_url = get_artist_image(sp, artist_id)

    # Fetch dominant colors from the artist image
    artist_color = None
    if artist_image_url:
        dominant_colors = get_dominant_colors(artist_image_url)
        if dominant_colors:
            # Assuming you want to use the most dominant color (the first one)
            artist_color = dominant_colors[0]  # This will be an RGB tuple

    # Fetch albums
    albums = get_artist_albums(sp, artist_id)

    # Fetch top tracks
    topsongs = get_artist_top_tracks(sp, artist_id)

    # Fetch additional artist description
    description = fetch_artist_description(artist_name)

    # Convert artist_color to a string format for database storage
    if artist_color is not None:
        artist_color = f"RGB({artist_color[0]}, {artist_color[1]}, {artist_color[2]})"  # Or use hex format

    # Update or create the artist instance
    artist, created = Artist.objects.update_or_create(
        slug=slugify(artist_name),
        defaults={
            'name': artist_name,
            'description': description,
            'image_url': artist_image_url,
            'banner_color': artist_color
        }
    )

    print(f"{'Created' if created else 'Updated'} artist: {artist.name}, banner_color: {artist.banner_color}")  # Debugging line

    # Return structured data
    return {
        'description': description,
        'topsongs': topsongs,
        'albums': albums,
        'image_url': artist_image_url,
        'banner_color': artist_color
    }



def get_artist_id(sp, artist_name):
    search_results = sp.search(q=artist_name, type='artist')
    return search_results['artists']['items'][0]['id']

def get_artist_image(sp, artist_id):
    """Fetch the artist's image."""
    try:
        artist = sp.artist(artist_id)
        image_url = artist['images'][0]['url'] if artist['images'] else None
        print(f"Fetched image URL: {image_url}")  # Debugging line
        return image_url
    except Exception as e:
        print(f"Error fetching artist image: {e}")
        return None

def get_dominant_colors(image_url, n_clusters=5):
    """Gets the most vibrant dominant colors in an image from a URL.

    Args:
        image_url (str): The URL to the image.
        n_clusters (int): The number of dominant colors to extract.

    Returns:
        list: A list of RGB color tuples, or None if there is an error.
    """
    try:
        # Fetch the image data from the URL
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful

        # Convert the image data to a NumPy array
        image = Image.open(BytesIO(response.content))  # Use BytesIO to handle the binary data
        image = image.resize((100, 100))  # Resize for faster processing
        image_array = np.array(image)

        # Reshape the array to a 2D array of pixels
        pixels = image_array.reshape(-1, 3)

        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(pixels)

        # Get the cluster centers (dominant colors)
        dominant_colors = kmeans.cluster_centers_.astype(int)

        # Function to convert RGB to HLS
        def rgb_to_hls(rgb):
            return colorsys.rgb_to_hls(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)

        # Find the most vibrant color based on saturation and brightness
        vibrant_color = max(dominant_colors, key=lambda color: rgb_to_hls(color)[1] * rgb_to_hls(color)[2])  # Max by (lightness * saturation)

        return [tuple(vibrant_color)]  # Return the most vibrant color as a single tuple
    except Exception as e:
        print(f"Error getting dominant colors: {e}")
        return None

def get_artist_albums(sp, artist_id):
    try:
        albums = sp.artist_albums(artist_id, album_type='album')
        formatted_albums = []
        for album in albums['items']:
            release_year = album['release_date'].split('-')[0]
            album_art = album['images'][0]['url'] if album['images'] else None
            formatted_albums.append({
                'title': album['name'],
                'release_date': release_year,
                'album_art': album_art
            })
        return formatted_albums[::-1]
    except Exception as e:
        return f"Error fetching albums: {e}"

def get_artist_top_tracks(sp, artist_id):
    try:
        top_tracks = sp.artist_top_tracks(artist_id, country='US')
        formatted_tracks = []
        
        # Collect all top tracks into a list
        track_ids = [track['id'] for track in top_tracks['tracks']]
        
        # Fetch track details in chunks
        for track_chunk in chunked(track_ids, 100):
            attempt = 0
            while attempt < 5:  # Retry up to 5 times
                try:
                    track_details = sp.tracks(track_chunk)  # Fetching track details for chunk
                    for track in track_details['tracks']:
                        release_year = track['album']['release_date'].split('-')[0]
                        album_art = track['album']['images'][0]['url'] if track['album']['images'] else None
                        formatted_tracks.append({
                            'title': track['name'],
                            'release_date': release_year,
                            'album_art': album_art,
                        })
                    break  # Break out of the retry loop if successful
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        retry_after = int(e.response.headers.get('Retry-After', 1))
                        print(f"Rate limited. Retrying after {retry_after} seconds.")
                        time.sleep(retry_after + 1)
                        attempt += 1
                    else:
                        print(f"HTTP error occurred: {e}")
                        break  # Exit on non-429 error
                except Exception as e:
                    print(f"Failed to get track details for chunk: {e}")
                    break  # Exit on other exceptions

            time.sleep(1)  # Sleep after processing a chunk

        return formatted_tracks
    except Exception as e:
        return f"Error fetching top tracks: {e}"

def fetch_artist_description(artist_name):
    artist_slug = artist_name.replace(' ', '-').lower()
    url = f"https://genius.com/artists/{artist_slug}/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the artist description using the appropriate class or tag
        description_div = soup.find("div", class_="rich_text_formatting")
        if description_div:
            description_text = description_div.get_text(separator="\n").strip()
            return format_description(description_text)
        else:
            return "Artist description not found."
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred for {artist_name}: {e}")
        return None

def format_description(description_text):
    # Convert album titles and major keywords to bold
    description_text = re.sub(r'(\b(?:Bastard|Goblin|Wolf|Cherry Bomb|Flower Boy|Music Inspired by Illumination & Dr. Seuss\' The Grinch|IGOR|CALL ME IF YOU GET LOST|CHROMAKOPIA)\b)', r'**\1**', description_text)
    
    # Use line breaks for readability around each album/project section
    description_text = re.sub(r'(\b(?:Bastard|Goblin|Wolf|Cherry Bomb|Flower Boy|Music Inspired by Illumination & Dr. Seuss\' The Grinch|IGOR|CALL ME IF YOU GET LOST|CHROMAKOPIA)\b)', r'\n\n\1', description_text)
    
    # Make headlines for major segments
    description_text = re.sub(r'(\b(?:Tyler Gregory Okonma|Known for his|On November 16, 2018|On May 17, 2019|On June 25, 2021|Tyler’s eighth project)\b)', r'\n\n\1', description_text)
    
    # Format dates
    description_text = re.sub(r'\b(\d{4})\b', r'\1', description_text)
    
    # Clean extra spaces and line breaks
    description_text = re.sub(r'\n{3,}', r'\n\n', description_text).strip()
    
    return description_text
