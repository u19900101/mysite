from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, render_to_response, get_object_or_404
from django.conf import settings
# Create your views here.
from comment.forms import CommentForm
from comment.models import Comment
from read_statistics.utils import read_statistics_once_read
from user.forms import LoginForm
from .models import Blog, BlogType, ReadNum


def get_blog_list_common_data(request,blogs_all_list):

    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每十页进行分页
    page_num = request.GET.get('page', 1)  # 字典，如果没有默认给1,获取页码参数
    page_of_blogs = paginator.get_page(page_num)

    current_page_num = page_of_blogs.number  # 获取当前页码
    # page_range = [current_page_num - 2, current_page_num - 1, current_page_num, current_page_num + 1, current_page_num + 2]
    page_range = list(range(max(current_page_num - 2, 1), min(current_page_num + 2, paginator.num_pages) + 1))

    # 加上省略页码标记
    if page_range[0] - 1 >= 2:  # 3-1>=2 第5页开始
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append("...")  # 15<=17-2

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    content = {}
    content["page_range"] = page_range
    # content["blogs"]=Blog.objects.all()
    content["blogs_count"] = blogs_all_list.count()

    '''blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    content["blog_types"] = blog_types_list'''
    content["blog_types"] = BlogType.objects.annotate(blog_count=Count('blog'))

    content["page_of_blogs"] = page_of_blogs

    blog_dates = Blog.objects.dates('created_time', 'day', order="DESC")
    blog_dates_list1={}
    for blog_date in blog_dates:
        year=blog_date.year
        month=blog_date.month
        day=blog_date.day
        count=Blog.objects.filter(created_time__year=year,created_time__month=month,created_time__day=day).count()
        blog_dates_list1[blog_date]=count

    content["blog_dates_list"] = blog_dates_list1
    blog_dates_list={}
    for k,v in blog_dates_list1.items():
        blog_dates_list[str(k)]=v

    return content
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    content=get_blog_list_common_data(request,blogs_all_list)
    return render_to_response('blog/blog_list.html',content)

def blog_detail(request,blog_pk):
    content ={}
    blog=get_object_or_404(Blog,pk=blog_pk)

    #blog_content_type = ContentType.objects.get_for_model(blog)
    #comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk,parent=None)
    #content['comments'] = comments.order_by('-comment_time')
    read_cookie_key = read_statistics_once_read(request, blog)
    content["blog"] = blog
    content["previous_blog"] = Blog.objects.filter(created_time__gt=blog.created_time).last()  # [-1]
    content["next_blog"] = Blog.objects.filter(created_time__lt=blog.created_time).first()  # [0]
    #content["login_form"] = LoginForm()
    #content["comments_count"] = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk).count()
    #content['comment_form'] = CommentForm(initial={'content_type': blog_content_type.model, 'object_id': blog_pk, 'reply_comment_id': 0})

    #content["user"] = request.user
    response = render(request,"blog/blog_detail.html", content)  # 响应
    response.set_cookie(key=read_cookie_key,value='true')  # 保存相关数据dict,有效期60秒,如果默认则是浏览器关闭cookie失效 ,max_age=60,expires=datetime
    return response

def blogs_with_type(request,blog_type_pk):

    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    content = get_blog_list_common_data(request, blogs_all_list)
    content['blog_type'] = blog_type
    return render_to_response('blog/blogs_with_type.html', content)

def blogs_with_date(request,year,month,day):
    blogs_all_list = Blog.objects.filter(created_time__year=year,created_time__month=month,created_time__day=day)
    content = get_blog_list_common_data(request, blogs_all_list)
    content["blogs_with_date"] = "%s年%s月%s日" % (year,month,day)
    return render_to_response('blog/blogs_with_date.html',content)