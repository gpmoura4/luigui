from rest_framework import serializers
from api.models import Database, Table,QuestionAnswer

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
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = [
                # "user_id",
                "database",
                "question"
                ]
class CompleteQASerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = [
                # "user_id",
                "database",
                "question",
                "answer",
                "query"
                ]
        