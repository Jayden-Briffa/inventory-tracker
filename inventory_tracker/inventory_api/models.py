from django.db import models
import uuid

# Create your models here.
class Item(models.Model):
    qrCode = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255)
    description = models.CharField(max_length = 255)
    isCollection = models.BooleanField(default=False)

# TODO: Add bulk force return
class Borrow(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    date = models.DateField(auto_now_add=True)
    expectedReturn = models.DateField()
    isReturned = models.BooleanField(default=False)