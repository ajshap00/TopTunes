from django.db import models
from django.utils.text import slugify
from .data import get_data
    

class Artist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    banner_color = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, editable=False)
    votes = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Artist, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Vote(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artist_votes')
    #user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes') WIP
    vote_text = models.CharField(max_length=200, blank=True, null=True)

    #class Meta:
    #    unique_together = ('artist', 'user') WIP

    def __str__(self):
        return self.vote_text or "No comment"
    
class Option(models.Model):
    option_text = models.CharField(max_length=200)
    vote = models.ForeignKey(Vote, null=True, on_delete=models.CASCADE, related_name='options')
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.option_text

class Song(models.Model):
    title = models.CharField(max_length=100)
    release_date = models.DateField()
    album_art = models.URLField(default='http://example.com/placeholder.jpg')
    artist = models.ForeignKey(Artist, related_name='topsongs', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Album(models.Model):
    title = models.CharField(max_length=100)
    release_date = models.DateField() 
    album_art = models.URLField(default='http://example.com/placeholder.jpg')
    artist = models.ForeignKey(Artist, related_name='albums', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
