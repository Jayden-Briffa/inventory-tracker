from django.db import models
import uuid

# Create your models here.
class Item(models.Model):
    itemId = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable = False,
    )
    qrCode = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255)
    description = models.CharField(max_length = 255)
    isCollection = models.BooleanField(default=False)

class Borrow(models.Model):
    borrowId = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable = False,
    )
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)
    date = models.DateField()
    expectedReturn = models.DateField()
    isReturned = models.BooleanField(default=False)