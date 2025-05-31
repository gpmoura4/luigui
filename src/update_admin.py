import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# Atualiza o usuário narutoAdmin
user = User.objects.get(username='narutoAdmin')
user.is_staff = True
user.is_superuser = True
user.save()

print(f"Usuário {user.username} atualizado com sucesso!")
print(f"is_staff: {user.is_staff}")
print(f"is_superuser: {user.is_superuser}") 