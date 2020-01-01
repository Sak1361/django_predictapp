from django.contrib import admin
from .models import Photo


@admin.register(Photo)
class ItemAdmin(admin.ModelAdmin):
    pass
