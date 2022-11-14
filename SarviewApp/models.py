from datetime import datetime
from django.db import models

#Modelo de los datos de rodion actualmente en desuso
class rodion(models.Model):
    datetime=models.DateField()
    tachometer1 = models.FloatField()
    temperature1 = models.FloatField()
    tachometer2 = models.FloatField()
    temperature2 = models.FloatField()
    tachometer3 = models.FloatField()
    temperature3 = models.FloatField()
    
