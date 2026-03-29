from django.urls import path
from AdminApp import views
urlpatterns=[
    path('login', views.adminlogin),
    path('logaction', views.logaction),
    path('AdminHome', views.AdminHome),
    path('UploadDataset', views.UploadDataset),
    path('Preprocess', views.Preprocess),
    path('runCNN', views.runCNN),

]
