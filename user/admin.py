from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, UserAdmin
from django.contrib.auth.models import User
from user.models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines=(ProfileInline,)
    list_display =('username', 'nickname','email','is_staff','is_active','is_superuser')
    def nickname(self,obj):
        return obj.profile.nickname
    nickname.short_description = '昵称1'
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_dispaly = ('user','nikename')