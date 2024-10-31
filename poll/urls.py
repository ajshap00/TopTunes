from django.urls import path
from . import views

app_name = 'poll'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('artists/<slug:slug>/', views.artist_detail, name='artist_detail'),
    path('artists/', views.artist_page, name='artists'),
    path('vote/', views.vote_page, name='vote'),
    path('results/', views.voted_page, name='results'),
    path('search/', views.search_results, name='search'),
]