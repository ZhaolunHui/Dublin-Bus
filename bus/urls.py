from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='bus_test-home'),
    path('my-ajax-test/', views.findroutedetails, name='findroutedetails'),
    path('my-nearest-bus-stop/',views.getnearestbusstops,name = 'getnearestbusstops'),  
    path('my-tourist-places/',views.getalltouristplaces,name = 'getalltouristplaces'),
    
    
]