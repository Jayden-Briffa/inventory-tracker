from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from .models import Item, Borrow
from .serializers import ItemSerializer
from django.shortcuts import HttpResponse
from django.views import View

# Create your views here.
# @method_decorator(csrf_exempt, name="dispatch")
class ItemCreate(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    querySet = Item.objects.all()
    serializer_class= ItemSerializer
    lookup_field = "pk"