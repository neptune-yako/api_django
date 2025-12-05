from django.contrib import admin
from .models import User, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """后台用户列表设置"""
    list_display = ['id', 'username', 'nickname', 'email', 'mobile', 'is_staff', 'is_active', 'is_superuser',
                    'date_joined', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_display_links = ('username',)
    list_filter = ('username',)
    search_fields = ('username',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """后台角色列表设置"""
    list_display = ['id', 'name', 'description', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


# 设置后台网页、登录页、内置页标题名称
admin.site.site_header = '后台管理系统'
admin.site.site_title = '后台管理'
admin.site.index_title = '后台管理系统'
