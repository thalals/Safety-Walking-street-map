from django.shortcuts import render
from . import models

# Create your views here.
def home(request):
    designer = models.Designer.objects.all()
    print(designer)
    return render(request,'home.html', {'designer' : designer})