from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
# Create your models here.
from django.urls import reverse

from read_statistics.models import ReadNum, ReadNumExpandMethod, ReadDetail


class BlogType(models.Model):
    type_name=models.CharField(max_length=15)
    def __str__(self):
        return "{}".format(self.type_name)

class Blog(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType,on_delete=models.CASCADE)
   # readed_num= models.IntegerField(default=0)
    read_details = GenericRelation(ReadDetail)
    content = RichTextUploadingField()
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    created_time=models.DateTimeField(auto_now_add=True)
    last_updated_time=models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_email(self):
        return self.author.email

    def __str__(self):
        return "Blog：{}".format(self.title)

    '''def read_num(self):
        try:
            ct=ContentType.objects.get_for_model(Blog)
            readnum=ReadNum.objects.get(content_type=ct,objetc_id=self.pk)
            return readnum.read_num
        except Exception as e:
            return 0'''

    class Meta:
        ordering=['-created_time']

'''class ReadNum(models.Model):
    read_num= models.IntegerField(default=0)
    blog=models.OneToOneField(Blog,on_delete=models.CASCADE)'''