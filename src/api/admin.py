from django.contrib import admin
from api.models import Database, Table, QuestionAnswer


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
   pass

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
   pass

@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
   pass