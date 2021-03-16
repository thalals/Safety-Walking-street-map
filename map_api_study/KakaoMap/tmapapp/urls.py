from django.urls import path
from . import views

urlpatterns = [
    path('tmap',views.thome, name='thome'),
    path('pathFinder/',views.pathFinder,name='pathFinder'),#길찾기 구 반환
    path('normalPath/',views.normalPath,name='normalPath'),#일반 길찾기
    path('hardPath/',views.aStar,name='aStar'),#우회 길찾기
    path('tsample',views.tsample, name='tsample'),


]
