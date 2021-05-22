from django.urls import path
from . import views

urlpatterns = [
    path('tmap',views.thome, name='thome'),
    path('pathfinder/',views.pathSetting,name='pathSetting'),
    path('pathFinder/',views.pathFinder,name='pathFinder'),#길찾기 구 반환
    path('normalPath/',views.normalPath,name='normalPath'),#일반 길찾기
    path('hardPath/',views.origin_Astar,name='aStar'),#우회 길찾기
    path('tsample',views.tsample, name='tsample'),

    path('grid_draw/',views.gird_draw, name='grid_draw') #그리드 그리기

]
