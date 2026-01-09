from app.document_api.document_api import main
from flask import Flask
from .event_payload import set_up_api

app = Flask(__name__)

class TestDlmeApi():

    def test_list_document_types(self) -> None:
        query_param = {"cnpj": "76575675675676"}
        body = "{\"key\":\"value\"}"
        event = set_up_api('/document/list/document_types','GET',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 200

    def test_list_documents(self) -> None:
        query_param = {"document_type_id": "3f0343b5-e8ae-4a22-ba79-e930319b825a"}
        body = "{\"key\":\"value\"}"
        event = set_up_api('/document/list/files','GET',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 200

    def test_list_palavra_chave(self) -> None:
        query_param = {}
        body = "{\"key\":\"value\"}"
        event = set_up_api('/document/list/palavra_chave','GET',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 200

    def test_create_palavra_chave(self) -> None:
        query_param = {"cnpj": "76575675675676"}
        body = "{\"palavra\":\"value\"}"
        event = set_up_api('/document/create/palavra_chave','POST',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 201
            
    def test_create_doc_anexo(self) -> None:
        query_param = {}
        body = "{\"id_documento\":\"5347ef0a-d2cf-44b8-9ea5-7274a2c5ff28\",\"id_anexo\":\"31d82fb8-e056-415e-a3b4-fb1e95a92c18\"}"
        event = set_up_api('/document/create/documento_anexo','POST',query_param, body)
        with app.app_context():
            response = main(event,'')
            print(response)
            assert response['statusCode'] == 201
            
    def test_delete_doc_anexo(self) -> None:
        query_param = {}
        event = set_up_api('/document/delete/documento_anexo/dc8474f0-6766-4316-8ff2-173741ca3c6d','DELETE',query_param, None)
        with app.app_context():
            response = main(event,'')
            print(response)
            assert response['statusCode'] == 400
            
            