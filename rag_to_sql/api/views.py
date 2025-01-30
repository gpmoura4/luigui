# from django.http import HttpResponse
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Database
from api.serializer import  DatabaseSerializer


class DatabaseList(APIView):
    def get(self, request, format=None):
        databases = Database.objects.all()
        serializer = DatabaseSerializer(databases, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = DatabaseSerializer(data = request.data)
        if serializer.is_valid():
            dbName = DatabaseSerializer.Meta.fields[0]
            print("O NOME É: ",dbName)
            # db = DatabaseSerializer.Meta()
            # db.name = serializer.validated_data.get('name', db.name)
            # db.username = serializer.validated_data.get('username', db.username)
            
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)    

class DatabaseDetail(APIView):
    def get_object(self, pk):
        try:
            return Database.objects.get(pk=pk)
        except Database.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        database = self.get_object(pk)
        serializer = DatabaseSerializer(database)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        database = self.get_object(pk)
        serializer = DatabaseSerializer(database, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        database = self.get_object(pk)
        database.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
