from django.db import models

# Create your models here.

# o que o usuario precisa pra cadastrar o banco
# senha 
# link do banco?
# email do user
# 
class Database(models.Model):
    user = models.CharField(max_length=200)

    db_name = models.CharField(max_length=200)

    db_url_acess = models.CharField(max_length=500)