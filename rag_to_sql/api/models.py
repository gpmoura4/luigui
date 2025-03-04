from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User


class Database(models.Model):
    name = models.CharField(max_length=255, verbose_name='Database Name')
    username = models.CharField(max_length=255, verbose_name='Database Username')
    password = models.CharField(max_length=255, verbose_name='Database Hashed Password')
    port = models.PositiveIntegerField(verbose_name='Database Port')
    host = models.CharField(max_length=255, verbose_name='Database Host')
    have_obj_index = models.BooleanField(default=False, verbose_name='Have Object Index')

    def __str__(self):
        return str(self.id)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Table(models.Model):
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Table Name')

    def __str__(self):
        return self.name
    

class QuestionAnswer(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    question = models.TextField( verbose_name='User Natural Language Question')
    answer = models.TextField( verbose_name='RAG Answer', null=True, blank=True)
    query = models.TextField( verbose_name='SQL Query', null=True, blank=True)
