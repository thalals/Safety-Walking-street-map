from django.shortcuts import render, HttpResponseRedirect
from django.views.generic.edit import UpdateView
from . import models
#CBV 사용
from django.views.generic import CreateView,ListView, DeleteView

# # fbv.
# def home(request):
#     designer = models.Designer.objects.all()
#     print(designer)
#     return render(request,'home.html', {'designer' : designer})


#cbv
#Read(게시물 나열)
class DesignerList(ListView):
    model = models.Designer
    context_object_name = 'designer'   #객체를 부르는 이름
    template_name='home.html'    #Default 연결 값 변경


#Create(게시물 생성)
class DesignerCreate(CreateView):
    model = models.Designer
    fields = ['image', 'name', 'adress', 'description',] #ModelForm을 안써줄때 자동 생성, form_class랑 같이사용시 에러
    success_url='/' # or reverse_lazy('designer') url 이름
    template_name='create2.html'

    def form_valid(self, form):
        designer = form.save(commit=False)
        designer.adress =form.cleaned_data['image']
        
        designer.save()
        return super().form_valid(form)
        # return HttpResponseRedirect(self.get_success_url())

#Delete(게시물 삭제)
class DesignerDelete(DeleteView) :
    model = models.Designer
    template_name ='delete.html'
    success_url='/' # or reverse_lazy('designer') url 이름


#Update(게시물 수정)
class DesignerUpdate(UpdateView):
    model = models.Designer
    fields = ['image', 'name', 'adress', 'description',]
    template_name='update.html'
    success_url='/' # or reverse_lazy('designer') url 이름

    # def form_valid(self, form):
    #     designer = form.save(commit=False)
    #     designer.adress =form.cleaned_data['image']
        
    #     designer.save()
    #     return super().form_valid(form)

    