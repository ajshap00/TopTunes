from django.contrib import admin
from .models import Artist, Song, Album

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'banner_color', 'image_url')

    search_fields = ('name',)
    list_filter = ('banner_color',)

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song)
admin.site.register(Album)
