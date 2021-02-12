from django import urls
from django.urls import path

from . import views

urlpatterns = [
    # path('',views.home, name ='home'),
    path('',views.DesignerList.as_view(), name='designer'),
    path('home',views.go, name='go'),
    path('create',views.DesignerCreate.as_view, name='create'),
]
