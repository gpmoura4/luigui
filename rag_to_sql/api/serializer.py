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


# arquivo serializer.py
class DatabaseSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user = serializers.HiddenField(  # Alteração aqui: campo oculto com valor padrão
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Database
        fields = [
            "user",  # Mantido nos campos
            "id",
            "name", 
            "username", 
            "password", 
            "port", 
            "host"
        ]

    def create(self, validated_data):
        # Extrai a senha antes de criar o objeto
        raw_password = validated_data.pop('password')
        
        # Cria a instância JÁ INCLUINDO o user do validated_data
        database = Database.objects.create(**validated_data)
        
        # Define a senha hasheada
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
        fields = ["database", "question", "answer", "query"]
        extra_kwargs = {
            "answer": {"read_only": True},
            "query": {"read_only": True},
        }