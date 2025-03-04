# from django.http import HttpResponse
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Database, Table, QuestionAnswer
from api.serializer import DatabaseSerializer, TableSerializer, QuestionAnswerSerializer
from api import schemas
from api.services.rag_service import *
from django.forms.models import model_to_dict
import asyncio


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
    def post(self, request, database, format=None):
        try:
            db_obj = Database.objects.get(id=database)
            database_dict = model_to_dict(db_obj)
        except:
            return Response({"ERROR": "Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        data = request.data

        try: 
            db_password = data["db_password"]
        except:
            return Response({"ERROR": "db_password password not provided"}, status=status.HTTP_400_BAD_REQUEST)     
        table_name = data.get("name")
        if db_obj.table_set.filter(name=table_name).exists():
            return Response({"ERROR": "Table with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        data["database"] = database_dict["id"]
        data.pop("db_password", None)
        table_serializer = TableSerializer(data=data)
        if table_serializer.is_valid(): 
            if db_obj.check_password(db_password):
                database_dict["password"] = db_password
                connection_string = schemas.DatabaseConnection(**database_dict)    
                tables = [table.name for table in db_obj.table_set.all()]
                retriever = SQLTableRetriever(cnt_str=connection_string, tables=tables, have_obj_index=db_obj.have_obj_index)
                retriever.add_table_schema(table_serializer.validated_data["name"])
                table_serializer.save() 
                if not db_obj.have_obj_index:
                    db_obj.have_obj_index = True
                    db_obj.save()

            return Response(table_serializer.data, status=status.HTTP_201_CREATED)
        return Response(table_serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

    def get(self, request, database, format=None):
        # Buscar o id do db atual e listar todas as tabelas desse id    
        tables = Table.objects.filter(database=database)
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)
    



class TableDetail(APIView):
    def put(self, request, database, pk,  format=None):
        try: 
            db_obj = Database.objects.get(id=database)
        except:
            return Response({"ERROR":"Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        data = request.data 
        data["database"] = db_obj.id
        
        table = self.get_object(pk)
        serializer = TableSerializer(table, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, database, pk, format=None):
        try:
            db_obj = Database.objects.get(id=database)
            database_dict = model_to_dict(db_obj)
        except:
            return Response({"ERROR": "Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        
        connection_string = schemas.DatabaseConnection(**database_dict)    
        tables = [table.name for table in db_obj.table_set.all()]
        retriever = SQLTableRetriever(cnt_str=connection_string, tables=tables, have_obj_index=db_obj.have_obj_index)
        table = self.get_object(pk)
        print("-------- DELETE FUNCTION -------")
        print("table: ", table)
        print("table.name: ", table.name)
        retriever.delete_table_schema(table.name)
        table.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_object(self, pk):
        try:
            return Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            raise Http404
        
    def get(self, request, database, pk, format=None):
        table = self.get_object(pk)
        serializer = TableSerializer(table)
        return Response(serializer.data)


class QuestionAnswerList(APIView):    
    def post(self, request, database, format=None):
        print("starting post question answer list")
        try: 
            print("question answer try")
            db_obj = Database.objects.get(id=database)
            database_dict = model_to_dict(db_obj)
        except:
            return Response({"ERROR":"Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        data = request.data 
        try: 
            print("question answer try db_password")
            db_password = data["db_password"]    
        except:
            return Response({"ERROR": "db_password password not provided"}, status=status.HTTP_400_BAD_REQUEST)     

        
        data["database"] = db_obj.id
        # data["user_id"] = 5
        data.pop("db_password", None)
        serializer = QuestionAnswerSerializer(data=data)
        print("--------- view question linha 0")                
        if serializer.is_valid():            
            print("--------- view question linha 1")                
            if db_obj.check_password(db_password):
                database_dict["password"] = db_password
                connection_string = schemas.DatabaseConnection(**database_dict)    
                tables = [table.name for table in db_obj.table_set.all()]

                print("--------- view question linha 2")                
                
                response = asyncio.run(starts_workflow(
                    cnt_str=connection_string, 
                    tables=tables, 
                    user_question=data["question"],
                    have_obj_index=db_obj.have_obj_index
                ))
                print("VIEW response", response)
                print("--------- view question linha 3")
                serializer.validated_data["answer"] = response.response
                serializer.validated_data["query"] = response.query
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    def get(self, request, database, format=None):
        # Buscar o id do db atual e listar todas as tabelas desse id
        questions = QuestionAnswer.objects.filter(database=database)
        serializer = QuestionAnswerSerializer(questions, many=True)
        return Response(serializer.data)




        