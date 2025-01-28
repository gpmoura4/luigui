from django.contrib import admin
from api.models import Database


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
   pass
