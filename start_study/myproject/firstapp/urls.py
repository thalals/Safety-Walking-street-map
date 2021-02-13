from django import urls
from django.urls import path

from . import views

urlpatterns = [
    # path('',views.home, name ='home'),
    path('',views.DesignerList.as_view(), name='designer'),
    path('create',views.DesignerCreate.as_view(), name='create'),
    path('delete/<int:pk>',views.DesignerDelete.as_view(), name='delete'),
    path('update/<int:pk>',views.DesignerUpdate.as_view(), name='update'),

]
