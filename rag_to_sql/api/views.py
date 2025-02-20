# from django.http import HttpResponse
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Database, Table
from api.serializer import DatabaseSerializer, TableSerializer
from api import schemas
from api.services.rag_service import SQLTableRetriever
from django.forms.models import model_to_dict


class DatabaseList(APIView):
    def get(self, request, format=None):
        databases = Database.objects.all()
        serializer = DatabaseSerializer(databases, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = DatabaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   

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
            db_obj = Database.objects.get(id=db_id)
            database_dict = model_to_dict(db_obj)
            # database_dict = Database.objects.filter(id=db_id).values().first()
            # Database.check_password(password=password)
            # database_serializer = DatabaseSerializer(database)
            # database_serializer.is_valid()
        except:
            return Response({"ERROR": "Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        data = request.data

        try: 
            db_password = data["db_password"]
        except:
            return Response({"ERROR": "Database password not provided"}, status=status.HTTP_400_BAD_REQUEST)     
        
        data["db_id"] = database_dict["id"]
        data.pop("db_password", None)
        table_serializer = TableSerializer(data=data)
        if table_serializer.is_valid():
            # db_password = table_serializer.data["db_password"]

            table_serializer.save()
            
            if db_obj.check_password(db_password):
                database_dict["password"] = db_password
                connection_string = schemas.DatabaseConnection(**database_dict)
                retriever = SQLTableRetriever(connection_string)
                retriever.add_table_schema(schemas.TableInfo(table_name=table_serializer.data["name"]))
            return Response(table_serializer.data, status=status.HTTP_201_CREATED)
        return Response(table_serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

    def get(self, request, db_id, format=None):
        # Buscar o id do db atual e listar todas as tabelas desse id
        tables = Table.objects.filter(db_id=db_id)
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)



class TableDetail(APIView):
    def put(self, request, db_id, pk,  format=None):
        try: 
            database = Database.objects.get(id=db_id)
        except:
            return Response({"ERROR":"Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        data = request.data 
        data["db_id"] = database.id
        
        table = self.get_object(pk)
        serializer = TableSerializer(table, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, db_id, pk, format=None):
        table = self.get_object(pk)
        table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_object(self, pk):
        try:
            return Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            raise Http404
        
    def get(self, request, db_id, pk, format=None):
        table = self.get_object(pk)
        serializer = TableSerializer(table)
        return Response(serializer.data)


class QuestionAnswerList(APIView):    
    def post(self, request, db_id, format=None):
        try: 
            database = Database.objects.get(id=db_id)
        except:
            return Response({"ERROR":"Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        data = request.data 
        data["db_id"] = database.id
        serializer = TableSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    def get(self, request, db_id, format=None):
        # Buscar o id do db atual e listar todas as tabelas desse id
        tables = Table.objects.filter(db_id=db_id)
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)
