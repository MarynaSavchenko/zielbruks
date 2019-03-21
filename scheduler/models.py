from django.db import models

# Create your models here.
class Brukselki(models.Model):
    kolor = 'zielony'

    def __str__(self):
        self.kolor