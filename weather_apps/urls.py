from django.contrib import admin
from django.urls import path, register_converter
from . import views, converters

register_converter(converters.MyFloatConverter, 'my_float')

urlpatterns = [
    path('', views.index),
    path('<my_float:latitude>/<my_float:longitude>', views.weather, name='weather'),

]
