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
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Database
        fields = [
                "id",
                "name", 
                "username", 
                "password", 
                "port", 
                "host" 
                ]
    def create(self, validated_data):
        raw_password = validated_data.pop('password')
    
        # Cria a instância SEM salvar no banco
        database = Database(**validated_data)
    
        # Define a senha hasheada
        database.set_password(raw_password)
        
        # Salva apenas uma vez aqui
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