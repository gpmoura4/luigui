from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Database(models.Model):
    DATABASE_TYPE = (
        ('minimal', 'Minimal'),
        ('complete', 'Complete'),
    )

    user = models.ForeignKey(User, related_name='databases', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Database Name')
    type = models.CharField(max_length=10, choices=DATABASE_TYPE, default='complete')
    username = models.CharField(max_length=255, verbose_name='Database Username', blank=True, null=True)
    password = models.CharField(max_length=255, verbose_name='Database Hashed Password', blank=True, null=True)
    port = models.PositiveIntegerField(verbose_name='Database Port', blank=True, null=True)
    host = models.CharField(max_length=255, verbose_name='Database Host', blank=True, null=True)
    have_obj_index = models.BooleanField(default=False, verbose_name='Have Object Index')

    def __str__(self):
        return str(self.id)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
        
    def clean(self):    
        # Call the base class's clean() method to maintain default validation
        super().clean()

        # If type is 'complete', the connection fields are required.
        if self.type == 'complete':
            errors = {}
            if not self.username:
                errors['username'] = 'Username is required for complete connections.'
            if not self.password:
                errors['password'] = 'Password is required for complete connections.'
            if not self.host:
                errors['host'] = 'Host is required for complete connections.'
            if not self.port:
                errors['port'] = 'Port is required for complete connections.'
            if errors:
                raise ValidationError(errors)


class Table(models.Model):
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Table Name')

    def __str__(self):
        return self.name
    

class QuestionAnswer(models.Model):
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    question = models.TextField( verbose_name='User Natural Language Question')
    answer = models.TextField( verbose_name='RAG Answer', null=True, blank=True)
    query = models.TextField( verbose_name='SQL Query', null=True, blank=True)
