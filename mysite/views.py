from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.core.cache import cache
from blog.models import Blog
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data, \
    get_7_days_hot_blogs


def home(request):
    content = {}
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)
    # blogs=get_7_days_hot_blogs(blog_content_type)

    # 获取7天热门博客的缓存数据
    blogs = cache.get('hot_blogs_for_7_days')
    if blogs is None:
        blogs = get_7_days_hot_blogs(blog_content_type)
        cache.set('hot_blogs_for_7_days', blogs, 3600)
        print("计算得出数据")
    else:
        print("使用了缓存")

    content = {}
    content['dates'] = dates
    content['read_nums'] = read_nums
    content['today_hot_data'] = today_hot_data
    content['yesterday_hot_data'] = yesterday_hot_data
    content['blogs'] = blogs

    return render_to_response('home.html', content)


