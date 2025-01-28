from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Database(models.Model):
    name = models.CharField(max_length=255, verbose_name='Database Name')
    username = models.CharField(max_length=255, verbose_name='Database Username')
    password = models.CharField(max_length=255, verbose_name='Database Hashed Password')
    port = models.PositiveIntegerField(verbose_name='Database Port')
    host = models.CharField(max_length=255, verbose_name='Database Host')

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
