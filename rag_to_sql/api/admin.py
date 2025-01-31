from django.contrib import admin
from api.models import Database, Table


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
   pass
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
   pass
