from django import forms
from .models import Artist

class VoteForm(forms.Form):
    artist = forms.ModelChoiceField(queryset=Artist.objects.all(), empty_label="Choose an Artist")
