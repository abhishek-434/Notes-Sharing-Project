from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['full_name', 'college_name', 'course', 'department', 'semester', 'bio', 'profile_picture', 'email_verified']


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'get_full_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
