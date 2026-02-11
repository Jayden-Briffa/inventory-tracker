from django.contrib import admin
from .models import Item, Borrow

# Register your models here.
admin.site.register(Item)
admin.site.register(Borrow)