from django.contrib import admin
from .models import Photo
from .models import Schedule

admin.site.register(Schedule)
@admin.register(Photo)
class ItemAdmin(admin.ModelAdmin):
    pass
