from rest_framework import serializers
from api.models import Database, Table,QuestionAnswer
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    databases = serializers.PrimaryKeyRelatedField(many=True, queryset=Database.objects.all())

    class Meta:
        model = User
        fields = [
                "id",
                "username", 
                "databases"
                ]


class DatabaseSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Não obrigatório para 'minimal'
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    type = serializers.ChoiceField(choices=Database.DATABASE_TYPE)

    class Meta:
        model = Database
        fields = [
            "user",
            "id",
            "name",
            "type",
            "username",
            "password",
            "port",
            "host"
        ]

    def validate(self, data):
        # Se o tipo for 'complete', todos os campos de conexão são obrigatórios
        if data.get('type') == 'complete':
            errors = {}
            if not data.get('username'):
                errors['username'] = 'Username is required for complete connections.'
            if not data.get('password'):
                errors['password'] = 'Password is required for complete connections.'
            if not data.get('host'):
                errors['host'] = 'Host is required for complete connections.'
            if not data.get('port'):
                errors['port'] = 'Port is required for complete connections.'
            if errors:
                raise serializers.ValidationError(errors)
        
        return data

    def create(self, validated_data):
        # Remove a senha antes de criar o objeto
        raw_password = validated_data.pop('password', None)
        
        # Cria o objeto Database
        database = Database.objects.create(**validated_data)
        
        # Define a senha hasheada se for fornecida
        if raw_password:
            database.set_password(raw_password)
            database.save()
        
        return database
      
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = [
                "id",
                "name", 
                "database",
                ]
        
class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ["database", "question", "answer", "query", "prompt_type"]
        # Campos opcionais a depender do tipo de Database e prompt_type
        extra_kwargs = {
            "answer": {"read_only": True},
            "query": {"read_only": True},
        }