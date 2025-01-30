from rest_framework import serializers
from api.models import Database, Table

class DatabaseSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Database
        fields = [
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
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Table
        fields = [
                "name", 
                "db_id"
                ]
