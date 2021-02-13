from django.db import models

# Create your models here.
class Designer(models.Model) :  #models.Model은 고정(형식)
    ''' django models define '''
    
    image = models.ImageField(null=True, upload_to ="images/")  #미디어에 있는 images에 올릴거다
    name = models.CharField(max_length=50)
    adress = models.CharField(max_length=50)
    description = models.TextField()

    #생성되는 객체의 이름 object -> name
    def __str__(self) :
        return self.name