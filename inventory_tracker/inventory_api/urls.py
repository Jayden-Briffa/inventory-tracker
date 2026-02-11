from django.urls import path
from . import views

urlpatterns = [
    # QUESTION: Should api routes and DB fields be plural? Which casing?
    path("items/", views.ItemCreate.as_view(), name="item-view-create"),
    path("items/<int:pk>/", views.ItemRetrieveUpdateDestroy.as_view(), name="item-view-update")
]