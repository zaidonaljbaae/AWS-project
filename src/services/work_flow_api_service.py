#Services
from common.error_messages import *
from models.schema_dlm import TagWorkflow, TagAviso, Tag
from repositories.work_flow_repository import TagWorkFlowRepository, TagRepository, TagAvisoRepository
from repositories.public_repository import EmpresaRepository
from enums.default_return_messages import *
from common.custom_exception import CustomException
#Libs
from flask import jsonify, Response
from datetime import datetime, timezone


class WorkFlowApiService():
    def __init__(self, db_session):
        self.session = db_session
        self.tag_repository = TagRepository(db_session)
        self.tag_work_flow_repository = TagWorkFlowRepository(db_session)
        self.empresa_repository = EmpresaRepository(db_session)
        self.tag_aviso_repository = TagAvisoRepository(db_session)


    def create_tag(self, name, color, company_id,document_type_id, alerta):
        dup = self.tag_repository.get_first([Tag.Nome==name, Tag.IdEmpresa==company_id, Tag.IdTipoDocumento==document_type_id])
        if dup:
            raise CustomException((X_ALREADY_EXISTS).format('Tag'))
        alerta = alerta if alerta else None
        obj = Tag(name, color, company_id,document_type_id, alerta)
        self.tag_repository.add(obj)
        return CREATED, 201
    

    def create_tag_aviso(self,tag_id,email,aviso):
        obj = TagAviso(tag_id,email,aviso)
        self.tag_repository.add(obj)
        return CREATED, 201
    

    def create_tag_workflow(self, tag_orig_id, tag_dest_id, document_type_id, validation):
        dup = self.tag_work_flow_repository.get_first([TagWorkflow.IdTagOrig==tag_orig_id, TagWorkflow.IdTagDest==tag_dest_id,
                                                       TagWorkflow.IdTipoDocumento==document_type_id, TagWorkflow.Validacao==validation])
        if dup:
            raise CustomException((X_ALREADY_EXISTS).format('Branch'))
        
        sequencial = self.validate_tag_workflow(document_type_id,tag_orig_id, tag_dest_id)

        obj = TagWorkflow(tag_orig_id, tag_dest_id, sequencial, document_type_id, validation)
        self.tag_work_flow_repository.add(obj)
        return CREATED, 201

    def list_tag_workflow(self,page, per_page,document_type_id):
        response = self.tag_work_flow_repository.get_all_pagined(page, per_page,[TagWorkflow.IdTipoDocumento==document_type_id])
        return jsonify(response)

    def list_tag(self,page, per_page, document_type_id):
        response = self.tag_repository.get_all_tags(page, per_page,[Tag.IdTipoDocumento==document_type_id,Tag.Ativo==True, Tag.Excluido==False])
        return Response(response, mimetype='application/json')

    def list_tag_aviso(self,page, per_page, tag_id):
        response = self.tag_aviso_repository.get_all_pagined(page, per_page,[TagAviso.IdTag==tag_id])
        return response

    def validate_tag_workflow(self, document_type_id, tag_orig_id, tag_dest_id):
        # validar se a branch é ou não inicial e definir o sequencial do workflow a partir dela
        branch = self.tag_work_flow_repository.get_first([TagWorkflow.IdTipoDocumento==document_type_id,TagWorkflow.IdTagDest==tag_orig_id])
        if not branch:
            # RN - A branch inicial deve conter o mesmo ID para as tags origem e destino
            if tag_orig_id != tag_dest_id:
                raise CustomException(BAD_REQUEST, 400)
            else:
                sequencial=1
        else:
           sequencial=branch.Sequencial + 1
        
        # RN - a inclusão da branch não pode gerar loop em algum ramo anterior
        seq = sequencial
        while seq > 1:
            previous_wf = self.tag_work_flow_repository.get_first([TagWorkflow.IdTagDest == tag_orig_id, TagWorkflow.Sequencial == seq-1])
            seq = previous_wf.Sequencial
            tag_orig_id = previous_wf.IdTagOrig
            if previous_wf.IdTagOrig == tag_dest_id:
                raise CustomException((X_INVALID).format('branch'))
        return sequencial
    
    def delete_tagworkflow(self, id):
        tag_workflow = self.tag_work_flow_repository.get_first([TagWorkflow.Id == id])
        if tag_workflow is None:
            raise CustomException((X_NOT_FOUND).format(id + ': '))
        if tag_workflow.IdTagOrig == str(tag_workflow.IdTagDest):
            raise CustomException((X_INVALID).format('branch'))
        if tag_workflow:
            previous_branch = self.tag_work_flow_repository.get_first([TagWorkflow.IdTagOrig == str(tag_workflow.IdTagDest)])
            if previous_branch:
                raise CustomException((X_IN_WORKFLOW).format('Tag'))
        tag_workflow.DataAtualizacao = datetime.now(timezone.utc)
        tag_workflow.Ativo = False
        tag_workflow.Excluido = True
        return jsonify(tag_workflow.serialize())
    
    def delete_tag(self, id):
        tag = self.tag_repository.get_first([Tag.Id == id])
        workf = self.tag_work_flow_repository.get_first([TagWorkflow.IdTagDest==id])
        if workf:
            raise CustomException((X_IN_WORKFLOW).format('Tag'))
        if tag is None:
            raise CustomException((X_NOT_FOUND).format(id + ': '))

        tag.DataAtualizacao = datetime.now(timezone.utc)
        tag.Ativo = False
        tag.Excluido = True
        return jsonify(tag.serialize())
    
    def update_tag_work_flow(self,id,id_tag_orig,id_tag_dest):
        tag_work = self.tag_work_flow_repository.get_first([TagWorkflow.Id == id])
        if not tag_work:
            raise CustomException((X_NOT_FOUND).format('Branch'))
        tag_work.IdTagOrig = id_tag_orig
        tag_work.IdTagDest = id_tag_dest
        return SUCCESS, 200
    