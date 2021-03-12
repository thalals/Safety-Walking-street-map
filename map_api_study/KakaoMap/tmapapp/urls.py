from django.urls import path
from . import views

urlpatterns = [
    path('tmap',views.thome, name='thome'),
    path('pathfinder',views.pathfinder, name='pathFinder'),
    path('normalPath',views.normalPath, name='normalPath'),
    path('aStar',views.aStar, name='aStar'),
    path('tsample',views.tsample, name='tsample'),


]
