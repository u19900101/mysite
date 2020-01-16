from django.urls import path
from . import views
#start with blog
urlpatterns = [
    #http://lcolhost:8000/blog/1
    path('type/<int:blog_type_pk>',views.blogs_with_type,name="blogs_with_type"),
    path('<int:blog_pk>',views.blog_detail,name="blog_detail"),
    path('',views.blog_list,name="blog_list"),
    path('date/<int:year>/<int:month>/<int:day>',views.blogs_with_date,name="blogs_with_date"),

]