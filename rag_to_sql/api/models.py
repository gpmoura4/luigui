from django.db import models

# Create your models here.

# o que o usuario precisa pra cadastrar o banco
# senha 
# link do banco?
# email do user
# 
class Database(models.Model):
    name = models.CharField(max_length=255, verbose_name='Database Name')
    username = models.CharField(max_length=255, verbose_name='Database Username')
    password = models.CharField(max_length=255, verbose_name='Database Hashed Password')
    port = models.PositiveIntegerField(verbose_name='Database Port')
    host = models.CharField(max_length=255, verbose_name='Database Host')

