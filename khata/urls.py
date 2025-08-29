from django.urls import path
from khata import views

urlpatterns = [
    path('', views.home ),
    path('download_excel/',views.download_excel),
    path('manish/',views.manish),
    path('manish_export/',views.manish_export)
]
