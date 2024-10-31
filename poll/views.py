from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from .models import Artist, Vote, Song, Album
from .VoteForm import VoteForm
from .data import get_data
from django.db.models import Q

def home_page(request):
    return render(request, 'poll/home.html')

def search_results(request):
    query = request.GET.get('query', '')
    artists = Artist.objects.filter(name__icontains=query)[:10]
    artist_data = [
        {
            'name': artist.name,
            'image_url': artist.image_url,
            'slug': artist.slug,
        }
        for artist in artists
    ]

    return JsonResponse({'artists': artist_data})


def vote_page(request):
    if request.method == "POST":
        artist_id = request.POST.get('artist_id')
        voter_ip = request.META.get('REMOTE_ADDR')

        existing_vote = Vote.objects.filter(voter_ip=voter_ip).first()

        if existing_vote:
            return redirect('poll:results')
        else:
            try:
                artist = get_object_or_404(Artist, id=artist_id)
                vote = Vote(artist=artist, voter_ip=voter_ip)
                vote.save()

                artist.votes += 1
                artist.save()

                return redirect('poll:results')
            except IntegrityError:
                return HttpResponse("Error recording vote.")

    artists = Artist.objects.all()
    return render(request, 'poll/vote.html', {'artists': artists})

def voted_page(request):
    top_artists, bot_artists = get_artist_votes()
    top_artists = sorted(top_artists, key=lambda x: x[0].name)
    bot_artists = sorted(bot_artists, key=lambda x: x[0].name)
    return render(request, 'poll/voted.html', {
        'top_artists': top_artists,
        'bot_artists': bot_artists
    })

def get_artist_votes():
    artists = Artist.objects.all().order_by('-votes')
    artist_votes = [(artist, artist.votes) for artist in artists]
    top_artists = artist_votes[:50] 
    bot_artists = artist_votes[50:]
    return top_artists, bot_artists

def artist_page(request):
    artists = Artist.objects.all().order_by('-votes','name')
    return render(request, 'poll/artist_page.html', {'artists': artists})

def artist_detail(request, slug):
    artist = get_object_or_404(Artist, slug=slug)

    if artist.description and artist.albums.exists() and artist.topsongs.exists():
        artist_data = {
            'description': artist.description,
            'albums': list(artist.albums.all()),
            'topsongs': list(artist.topsongs.all())
        }
    else:
        artist_data = get_data(artist.name)

        artist.description = artist_data.get('description', '')
        artist.save()

    return render(request, 'poll/artist_detail.html', {
        'artist': artist,
        'description': artist_data.get('description', 'No description available.'),
        'albums': artist_data.get('albums', []),
        'topsongs': artist_data.get('topsongs', []),
    })
