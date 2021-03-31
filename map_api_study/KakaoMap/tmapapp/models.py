from django.db import models

# Create your models here.
#가로등 데이터(현재 광진구)
class Lamp(models.Model):
    name = models.AutoField(primary_key=True)
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        managed = False
        db_table = 'lamp'

class Roadtohexgrid(models.Model):
    objects = models.Manager()
    hexgrid_pk = models.AutoField(primary_key=True)
    hex_q = models.IntegerField()
    hex_r = models.IntegerField()
    hexgrid_loc = models.TextField(blank=True, null=True)  # This field type is a guess.
    hexgrid_gu = models.CharField(max_length=30, blank=True, null=True)
    is_danger = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'roadToHexgrid'

