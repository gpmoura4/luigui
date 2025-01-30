# from django.http import HttpResponse
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Database, Table
from api.serializer import  DatabaseSerializer, TableSerializer


class DatabaseList(APIView):
    def get(self, request, format=None):
        databases = Database.objects.all()
        serializer = DatabaseSerializer(databases, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
        serializer = DatabaseSerializer(data = request.data)
        if serializer.is_valid():
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

class TableList(APIView):
    
    def post(self, request, db_id, format=None):
        try: 
            database = Database.objects.get(id=db_id)
        except:
            return Response({"ERROR":"Database not found"}, status = status.HTTP_404_NOT_FOUND)    
        data = request.data
        data["db_id"] = database.id
        serializer = TableSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)    

    def get_object(self, pk):
        try:
            return Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        table = self.get_object(pk)
        serializer = DatabaseSerializer(table)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        table = self.get_object(pk)
        serializer = TableSerializer(table, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        table = self.get_object(pk)
        table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
