from django.urls import path
from . import views


urlpatterns = [
    path('update_comment', views.update_comment, name='update_comment'),
    path('get_face', views.get_face, name='get_face')
]