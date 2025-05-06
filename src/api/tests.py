from django.test import TestCase
from .models import Database


class DatabaseModelTest(TestCase):
    def test_create_database(self):
        db = Database(
            name="vector",
            port=5437,
            username="user"
        )
        db.set_password("pass")  # Hashea a senha usando Argon2
        db.save()

        # Verificar se foi salvo corretamente
        self.assertTrue(db.check_password("pass"))
