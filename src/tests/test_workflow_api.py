from app.work_flow_api.work_flow_api import main
from flask import Flask
from .event_payload import set_up_api

app = Flask(__name__)

class TestWFApi():


    def test_list_tag(self) -> None:
        query_param = {"document_type_id": "51666f1c-427f-4f50-8152-0f06e202662a"}
        body = "{\"key\":\"value\"}"
        event = set_up_api('/work_flow/list/tag','GET',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 200

    def test_list_tag_aviso(self) -> None:
        query_param = {"tag_id": "5646d5cd-6b37-474c-9820-af11630b68f8"}
        body = "{\"key\":\"value\"}"
        event = set_up_api('/work_flow/list/tag_aviso','GET',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 200

    def test_list_tag_workflow(self) -> None:
        query_param = {"document_type_id": "51666f1c-427f-4f50-8152-0f06e202662a"}
        body = "{\"key\":\"value\"}"
        event = set_up_api('/work_flow/list/tag_workflow','GET',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 200

    def test_create_tag(self) -> None:
        query_param = {}
        body = "{\"name\":\"tag_unit_test\",\"color\":\"test\",\"company_id\":\"7a0533c3-9fae-4a42-9cea-b211861bc5f1\",\"document_type_id\":\"18e84fc8-2d0f-4b8b-860c-b5a03cc5519e\"}"
        event = set_up_api('/work_flow/create/tag','POST',query_param, body)
        with app.app_context():
            response = main(event,'')
            assert response['statusCode'] == 201
            
    def test_create_tag_workflow(self) -> None:
        query_param = {}
        body = "{\"tag_orig_id\":\"03c98893-f3fc-4c62-80dd-cb904b75b5f4\",\"tag_dest_id\":\"03c98893-f3fc-4c62-80dd-cb904b75b5f4\",\"document_type_id\":\"3f0343b5-e8ae-4a22-ba79-e930319b825a\",\"validation\":true}"
        event = set_up_api('/work_flow/create/tag_workflow','POST',query_param, body)
        with app.app_context():
            response = main(event,'')
            print(response)
            assert response['statusCode'] == 201

    def test_create_tag_aviso(self) -> None:
        query_param = {}
        body = "{\"tag_id\":\"03c98893-f3fc-4c62-80dd-cb904b75b5f4\",\"email\":\"matheus@maketheway.tech\",\"aviso\":\"unit test\"}"
        event = set_up_api('/work_flow/create/tag_aviso','POST',query_param, body)
        with app.app_context():
            response = main(event,'')
            print(response)
            assert response['statusCode'] == 201
            
    #def test_delete_doc_anexo(self) -> None:
    #    query_param = {}
    #    event = set_up_api('/document/delete/documento_anexo/dc8474f0-6766-4316-8ff2-173741ca3c6d','DELETE',query_param, None)
    #    with app.app_context():
    #        response = main(event,'')
    #        print(response)
    #        assert response['statusCode'] == 400
            
            