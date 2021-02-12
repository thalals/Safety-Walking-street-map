from django.shortcuts import render
from . import models
#CBV 사용
from django.views.generic import CreateView,ListView

# # fbv.
# def home(request):
#     designer = models.Designer.objects.all()
#     print(designer)
#     return render(request,'home.html', {'designer' : designer})

def go(request):
    return render(request,'create.html')
#cbv
#Read(게시물 나열)
class DesignerList(ListView):
    model = models.Designer
    context_object_name = 'designer'   #객체를 부르는 이름
    template_name='home.html'    #Default 연결 값 변경


#Create(게시물 생성)
class DesignerCreate(CreateView):
    model = models.Designer
    context_object_name = 'designer'
    success_url='home.html'
    template_name='create.html'