# from django.http import HttpResponse
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Database, Table, QuestionAnswer
from api.serializer import DatabaseSerializer, TableSerializer, QuestionAnswerSerializer, UserSerializer
from api import schemas
from api.services.rag_service import *
from django.forms.models import model_to_dict
import asyncio
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from api.permissions import IsOwner, IsOwnerTable




class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# arquivo views.py
class DatabaseList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwner]
    
    def get(self, request, format=None):
        # Alteração: Filtra os databases pelo usuário autenticado
        if request.user.is_authenticated:
            databases = Database.objects.filter(user=request.user)
        else:
            databases = Database.objects.none()  # Retorna um queryset vazio se não estiver autenticado

        serializer = DatabaseSerializer(databases, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # Remove todas as manipulações manuais do user_id
        serializer = DatabaseSerializer(
            data=request.data,
            context={'request': request}  # Importante para o CurrentUserDefault
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
   

class DatabaseDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]  # Requer autenticação

    def get_object(self, pk):
        try:
            # Filtra o database pelo ID E pelo usuário autenticado
            return Database.objects.get(pk=pk, user=self.request.user)
        except Database.DoesNotExist:
            raise Http404  # Retorna 404 se não existir ou não pertencer ao usuário

    def get(self, request, pk, format=None):
        database = self.get_object(pk)  # Só chega aqui se o objeto existir e pertencer ao usuário
        serializer = DatabaseSerializer(database)
        return Response(serializer.data)

    # Mantenha os métodos PUT e DELETE conforme já existem

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
        # Deletar base de dados vetorial e as tables
        return Response(status=status.HTTP_204_NO_CONTENT)


class TableList(APIView):    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerTable]
    def post(self, request, database, format=None):
        # Validação da tabela
        try:
            db_obj = Database.objects.get(id=database)
            database_dict = model_to_dict(db_obj)
        except:
            return Response({"ERROR": "Database not found."}, status=status.HTTP_404_NOT_FOUND)    
        data = request.data
        if db_obj.type == "complete":
            try: 
                db_password = data["db_password"]
            except:
                return Response({"ERROR": "db_password password not provided."}, status=status.HTTP_400_BAD_REQUEST)     
            table_name = data.get("name")
            if db_obj.table_set.filter(name=table_name).exists():
                return Response({"ERROR": "Table with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Inserindo a tabela 
            data["database"] = database_dict["id"]
            data.pop("db_password", None)
            table_serializer = TableSerializer(data=data)
            if table_serializer.is_valid(): 
                if db_obj.check_password(db_password):
                    database_dict["password"] = db_password
                    connection_string = schemas.DatabaseConnection(**database_dict)    
                    tables = [table.name for table in db_obj.table_set.all()]
                    retriever = SQLTableRetriever(
                        cnt_str=connection_string, 
                        tables=tables, 
                        have_obj_index=db_obj.have_obj_index
                    )
                    retriever.add_table_schema(table_serializer.validated_data["name"])
                    table_serializer.save() 
                    if not db_obj.have_obj_index:
                        db_obj.have_obj_index = True
                        db_obj.save()
                return Response(table_serializer.data, status=status.HTTP_201_CREATED)       
                    # table_name = data.get("name")
        if db_obj.type == "minimal":
            # Apenas o campo schemas é obrigatório, mas os outros podem ficar null
            try: 
                only_schemas = data["schemas"]
            except:
                return Response({"ERROR": "schemas not provided."}, status=status.HTTP_400_BAD_REQUEST)     
            # Chamar a função para formatar o only_schemas para uma lista de schemas
            only_schemas_formatted = generate_postgres_schemas(only_schemas)
            for value in only_schemas_formatted:
                # subir o only_schemas_formatted para o PGVector
                retriever_schema =  SQLSchemaRetriever(value['table_name'])
                retriever_schema.add_table_schema(value['schema'])
                data = {}
                data["database"] = database_dict["id"]
                data["name"] = value['table_name']
                table_serializer = TableSerializer(data=data)
                if table_serializer.is_valid():
                    table_serializer.save()
                    return Response(table_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(table_serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
            
    
        

    
    def get(self, request, database, format=None):
        if request.user.is_authenticated:        
            print("IF USER TABLE request.user.is_authenticated:")
            try:
                user_database = Database.objects.get(pk=database, user=self.request.user)        
            except:
                return Response({"ERROR": "Not found."}, status=status.HTTP_400_BAD_REQUEST)     
        else:   
            print("ELSE USER TABLE")
            return Response({"ERROR": "User is not is_authenticated."}, status=status.HTTP_400_BAD_REQUEST)     
            databases = Database.objects.none()  # Retorna um queryset vazio se não estiver autenticado

        tables = Table.objects.filter(database=database)
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)
        # Buscar o id do db atual e listar todas as tabelas desse id    

class TableDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerTable]
    
    def get_object(self, database, pk):
        """
        Recupera a tabela garantindo que ela pertença ao database especificado e checa as permissões.
        """
        try:
            table = Table.objects.get(pk=pk, database__id=database)
            # Verifica as permissões para o objeto recuperado
            self.check_object_permissions(self.request, table)
            return table
        except Table.DoesNotExist:
            raise Http404

    def get(self, request, database, pk, format=None):
        table = self.get_object(database, pk)
        serializer = TableSerializer(table)
        return Response(serializer.data)  
    def put(self, request, database, pk, format=None):
        # Primeiro, verifica se o database existe
        try:
            db_obj = Database.objects.get(id=database)
        except Database.DoesNotExist:
            return Response({"ERROR": "Database not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Recupera a tabela com a verificação de permissão
        table = self.get_object(database, pk)
        
        # Atualiza os dados e garante que o campo "database" seja o ID correto
        data = request.data.copy()  # Faz uma cópia mutável dos dados
        data["database"] = db_obj.id
        
        serializer = TableSerializer(table, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, database, pk, format=None):
        # Primeiro, verifica se o database existe
        try:
            db_obj = Database.objects.get(id=database)
        except Database.DoesNotExist:
            return Response({"ERROR": "Database not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Recupera a tabela com a verificação de permissão
        table = self.get_object(database, pk)
        
        # Prepara a conexão para manipulação do schema da tabela
        database_dict = model_to_dict(db_obj)
        connection_string = schemas.DatabaseConnection(**database_dict)
        tables = [table_obj.name for table_obj in db_obj.table_set.all()]
        retriever = SQLTableRetriever(cnt_str=connection_string, tables=tables, have_obj_index=db_obj.have_obj_index)
        
        # Remove a definição do schema e deleta a tabela
        retriever.delete_table_schema(table.name)
        table.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


# class TableDetail(APIView):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerTable]
#     def put(self, request, database, pk,  format=None):
#         try: 
#             db_obj = Database.objects.get(id=database)
#         except:
#             return Response({"ERROR":"Database not found"}, status=status.HTTP_404_NOT_FOUND)    
#         data = request.data 
#         data["database"] = db_obj.id
        
#         table = self.get_object(pk)
#         serializer = TableSerializer(table, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
#     def delete(self, request, database, pk, format=None):
#         try:
#             db_obj = Database.objects.get(id=database)
#             database_dict = model_to_dict(db_obj)
#         except:
#             return Response({"ERROR": "Database not found"}, status=status.HTTP_404_NOT_FOUND)    
        
#         connection_string = schemas.DatabaseConnection(**database_dict)    
#         tables = [table.name for table in db_obj.table_set.all()]
#         retriever = SQLTableRetriever(cnt_str=connection_string, tables=tables, have_obj_index=db_obj.have_obj_index)
#         table = self.get_object(pk)
#         print("-------- DELETE FUNCTION -------")
#         print("table: ", table)
#         print("table.name: ", table.name)
#         retriever.delete_table_schema(table.name)
#         table.delete()

#         return Response(status=status.HTTP_204_NO_CONTENT)
    
#     def get_object(self, database_id, pk):
#         try:
#             # Garante que a tabela pertence ao database especificado
#             return Table.objects.get(pk=pk, database__id=database_id)
#         except Table.DoesNotExist:
#             raise Http404
        
#     def get(self, request, database, pk, format=None):
#         table = self.get_object(pk)
#         serializer = TableSerializer(table)
#         return Response(serializer.data)


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
                serializer.validated_data["query"] = response.sql_query
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    def get(self, request, database, format=None):
        # Buscar o id do db atual e listar todas as tabelas desse id
        questions = QuestionAnswer.objects.filter(database=database)
        serializer = QuestionAnswerSerializer(questions, many=True)
        return Response(serializer.data)




        