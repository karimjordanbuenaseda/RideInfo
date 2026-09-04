from django.contrib import admin
from core.models.user import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('id_user', 'role', 'first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('role',)
    ordering = ('-id_user',)