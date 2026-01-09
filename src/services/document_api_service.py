#Services
from common.error_messages import *
from models.schema_public import User
from models.schema_dlm import Documento, TipoDocumento, TagDocumento, PalavraChave, PalavraChaveDocumento, DocumentoAnexo, Grupo
from repositories.dlm_repository import *
from repositories.work_flow_repository import TagWorkFlowRepository, TagAvisoRepository, TagRepository
from repositories.public_repository import UserRepository
from enums.default_return_messages import *
from enums.status_enum import *
from common.custom_exception import CustomException
#Libs
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import jsonify, Response, g
import os
from datetime import datetime, timezone


EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

class DocumentoApiService():
    def __init__(self, db_session):
        self.session = db_session
        self.tag_repository = TagRepository(db_session)
        self.documento_repository = DocumentoRepository(db_session)
        self.tipo_documento_repository = TipoDocumentoRepository(db_session)
        self.tag_document_repository = TagDocumentoRepository(db_session)
        self.tag_work_flow_repository = TagWorkFlowRepository(db_session)
        self.tag_aviso_repository = TagAvisoRepository(db_session)
        self.palavra_chave_repository = PalavraChaveRepository(db_session)
        self.palavra_chave_documento_repository = PalavraChaveDocumentoRepository(db_session)
        self.documento_anexo_repository = DocumentoAnexoRepository(db_session)
        self.user_repository = UserRepository(db_session)
        self.arquivo_anexo_repository = ArquivoAnexoRepository(db_session)
        self.grupo_repository = GrupoRepository(db_session)      

    def get_document_by_id(self,id):
        response = self.documento_repository.get_first(Documento.Id == id)
        return jsonify(response)

    def list_document_by_document_type(self,page,per_page,document_type_id):
        response = self.documento_repository.get_all_by_type_id(page,per_page,document_type_id)
        return Response(response, mimetype='application/json')
    
    def get_document_type_by_id(self, id):
        response = self.tipo_documento_repository.get_first(TipoDocumento.Id == id)
        return jsonify(response)
        
    def list_document_type_by_cnpj(self, groupId, page, per_page):
        response = self.tipo_documento_repository.get_all_by_cnpj(groupId, page, per_page)
        return jsonify(response)

    def create_document_types(self,company_id,group_id,extensao,nome,sigla):
        obj_dup = self.tipo_documento_repository.get_first([TipoDocumento.Nome == nome, TipoDocumento.IdEmpresa == company_id, TipoDocumento.IdGrupo == group_id])
        if obj_dup:
            raise CustomException((X_ALREADY_EXISTS).format('Document type'))
        obj = TipoDocumento(company_id,group_id,extensao,nome,sigla)
        self.tipo_documento_repository.add(obj)
        return CREATED, 201
    
    def list_document_type_by_group(self, group):
        response = self.tipo_documento_repository.get_all(TipoDocumento.IdGrupo == group)
        return jsonify(response)
    
    def create_document_version(self,key,latest_document_id,versao):
        latest_obj = self.documento_repository.get_first([Documento.Id == latest_document_id])
        latest_obj.Latest = False
        latest_obj.Status = StatusEnum.CLOSED.value
        nome = key.split('/')[-1]
        v_param = {'V':{
                        'version':(latest_obj.Versao)+1,
                        'revision':0,
                        'patch':0
                        },
                   'R':{
                        'version':(latest_obj.Versao),
                        'revision':(latest_obj.Revisao)+1,
                        'patch':0
                        },
                   'P':{
                        'version':(latest_obj.Versao),
                        'revision':(latest_obj.Revisao),
                        'patch':(latest_obj.Patch)+1
                        }}

        version_obj = v_param[versao]
        status = StatusEnum.REQUEST_APPROVAL.value
        obj = Documento(nome,key,latest_obj.Numero,version_obj['version'],version_obj['revision'],version_obj['patch'],True,status,latest_obj.IdTipoDocumento, latest_obj.Observacao)
        self.documento_repository.add(obj)
        return CREATED, 201

    def create_document(self, key, document_type_id, descricao):
        info = key.split('/') if key else key
        document_name = info[-1] if info else None
        tipo_documento = self.tipo_documento_repository.get_first([TipoDocumento.Id == document_type_id])
        work_flow = self.tag_work_flow_repository.get_all([TagWorkflow.IdTipoDocumento == document_type_id])
        if not work_flow:
            raise CustomException((X_NOT_FOUND).format('WorkFlow'))
        
        response = self.documento_repository.get_first([Documento.Nome == document_name, Documento.IdTipoDocumento == document_type_id])
        if response:
            raise CustomException((X_ALREADY_EXISTS).format('Document'))
        
        status = StatusEnum.REQUEST_APPROVAL.value
        count = self.documento_repository.get_all_pagined(1,1,[Documento.IdTipoDocumento == document_type_id])
        count = count['total']

        obj = Documento(document_name, key, f'{tipo_documento.Sigla}-{count+1}', 1, 0, 0, True, status, document_type_id, descricao, g.user.Id)
        self.tipo_documento_repository.add(obj)
        return CREATED, 201

    def create_tag_document(self, document_id, tag_id):
        tag_doc_obj = self.tag_document_repository.get_first([TagDocumento.IdDocumento==document_id, TagDocumento.IdTag==tag_id])
        if tag_doc_obj:
            raise CustomException((X_ALREADY_EXISTS).format('tag'))
        else:
            # RN - Ao vincluar uma tag em um documento, validar se ela existe na tabela TagAviso e enviar o aviso
            tag_doc = TagDocumento(tag_id, document_id, g.user.Id)
            self.tag_document_repository.add(tag_doc)
            warnings = self.tag_aviso_repository.get_all([TagAviso.IdTag==tag_id])
            for wrn in warnings:
                self.enviar_email(wrn.Email,'DLM - Aviso', wrn.Aviso)
        return CREATED, 201

    def validate_tag_document(self,document_id,tag_id,validation, document_type_id, validacao_alerta):
        tag_wf_obj = self.tag_work_flow_repository.get_all([TagWorkflow.IdTagOrig==tag_id,TagWorkflow.Validacao==validation, 
                                                            TagWorkflow.IdTipoDocumento==document_type_id])
        current_tag = self.tag_document_repository.get_first([TagDocumento.IdDocumento==document_id,TagDocumento.IdTag==tag_id])
        current_tag.Excluido = True
        current_tag.Ativo = False
        alerts = []
        for item in tag_wf_obj:
            tag_dest_id = str(item.IdTagDest) if str(item.IdTagOrig) != str(item.IdTagDest) else None
            if tag_dest_id:
                tag = self.tag_repository.get_first([Tag.Id == tag_dest_id])
                if tag.Alerta and not validacao_alerta:
                    alerts.append(tag.serialize())
                else:
                    next_tag = TagDocumento(item.IdTagDest,document_id, g.user.Id)
                    self.tag_document_repository.add(next_tag)
        if alerts:
            return jsonify({"items":alerts})
        if not tag_wf_obj:
            doc_obj = self.documento_repository.get_first([Documento.Id==document_id])
            doc_obj.Status = StatusEnum.APPROVED.value
        return SUCCESS

    def enviar_email(self, destinatario, assunto, mensagem):
        remetente = "makeforward@maketheway.tech"
        senha = EMAIL_PASSWORD

        email = MIMEMultipart()
        email["From"] = remetente
        email["To"] = destinatario
        email["Subject"] = assunto

        corpo = MIMEText(mensagem, "plain")
        email.attach(corpo)

        servidor_smtp = "smtp.gmail.com"
        porta_smtp = 587

        try:
            conexao = smtplib.SMTP(servidor_smtp, porta_smtp)
            conexao.starttls()
            conexao.login(remetente, senha)
            conexao.sendmail(remetente, destinatario, email.as_string())
            print("E-mail enviado com sucesso!")

        except Exception as e:
            print("Ocorreu um erro ao enviar o e-mail:", str(e))

        finally:
            conexao.quit()
            
    def delete_table_document(self, id):
        document = self.documento_repository.get_first([Documento.Id == id])
        if document is None:
            raise CustomException((X_NOT_FOUND).format(id + ': '))

        document.DataAtualizacao = datetime.now(timezone.utc)
        document.Ativo = False
        document.Excluido = True
        return jsonify(document.serialize())
    
    def create_palavra_chave(self, palavra):
        response = self.palavra_chave_repository.get_first([PalavraChave.Palavra == palavra])
        if response:
            raise CustomException((X_ALREADY_EXISTS).format('Palavra Chave'))
        obj = PalavraChave(palavra)
        self.palavra_chave_repository.add(obj)
        return CREATED, 201    
    
    def create_palavra_chave_documento(self, id_palavra_chave, id_documento):
        response = self.palavra_chave_documento_repository.get_first([PalavraChaveDocumento.IdPalavraChave == id_palavra_chave, PalavraChaveDocumento.IdDocumento == id_documento])
        if response:
            raise CustomException((X_ALREADY_EXISTS).format('Palavra Chave Documento'))
        obj = PalavraChaveDocumento(id_palavra_chave, id_documento)
        self.palavra_chave_documento_repository.add(obj)
        return CREATED, 201
    
    def list_table_palavra_chave(self,page, per_page):
        response = self.palavra_chave_repository.get_all_pagined(page, per_page)
        return jsonify(response)
    
    
    def delete_palavra_chave(self, id):
        document = self.palavra_chave_repository.get_first([PalavraChave.Id == id])
        if document is None:
            raise CustomException((X_NOT_FOUND).format(id + ': '))

        document.DataAtualizacao = datetime.now(timezone.utc)
        document.Ativo = False
        document.Excluido = True
        return jsonify(document.serialize())

    def validate_document(self, document_id, status, alerta):
        documento = self.documento_repository.get_first([Documento.Id == document_id])
        if status == True:
            work_flow = self.tag_work_flow_repository.get_all([TagWorkflow.IdTipoDocumento == documento.IdTipoDocumento])
            alert = []
            obj_tag_document = None
            for branch in work_flow:
                if branch.IdTagOrig == str(branch.IdTagDest):
                    tag = self.tag_repository.get_first([Tag.Id == branch.IdTagOrig])
                    if tag.Alerta and not alerta:
                        alert.append(tag.serialize())
                        return jsonify({"items":alert})
                    else:
                        documento.Status = StatusEnum.PROCESSING.value
                        obj_tag_document = TagDocumento(branch.IdTagDest, documento.Id, g.user.Id)
            self.tag_document_repository.add(obj_tag_document)
        else:
            documento.Status = StatusEnum.CLOSED.value
        return SUCCESS, 201
    
    def create_doc_anexo(self, id_documento, id_anexo):
            response = self.documento_anexo_repository.get_first([DocumentoAnexo.IdAnexo == id_anexo, DocumentoAnexo.IdDocumento == id_documento])
            if response:
                raise CustomException((X_ALREADY_EXISTS).format('Documento anexo'))
            insert_obj = DocumentoAnexo(id_documento, id_anexo)
            self.documento_repository.add(insert_obj)
            return jsonify(insert_obj.serialize()), 201
        
    def delete_doc_anexo(self, id):
        doc_anexo = self.documento_anexo_repository.get_first([DocumentoAnexo.Id == id])
        if doc_anexo is None:
            raise CustomException((X_NOT_FOUND).format(id + ': '))

        doc_anexo.DataAtualizacao = datetime.now(timezone.utc)
        doc_anexo.Ativo = False
        doc_anexo.Excluido = True
        return jsonify(doc_anexo.serialize())
    
    def send_email(self, id_documento, list_emails, email_subject, email_body, name_update):
        if id_documento: #tag rejeitada.
            documento = self.documento_repository.get_first([Documento.Id == id_documento])
            user = self.user_repository.get_first([User.Id == documento.IdUsuarioCriacao])
            list_emails = user.Email
            email_subject = f"Arquivo {documento.Nome} recusado"
            self.enviar_email(list_emails, email_subject, f"{name_update} rejeitou o arquivo '{documento.Nome}', motivo: {email_body}")
        else:
            for email in list_emails:
                self.enviar_email(email, email_subject, email_body)
        return SUCCESS, 201
    
    def create_aquiv_anexo(self, id_documento, key):
        info = key.split('/')
        nome_arquivo = info[-1]
               
        response = self.arquivo_anexo_repository.get_first([ArquivoAnexo.Key == key])
        if response:
            raise CustomException((X_ALREADY_EXISTS).format('Document'))
        
        obj = ArquivoAnexo(id_documento,nome_arquivo, key)
        self.arquivo_anexo_repository.add(obj)
        return CREATED, 201
    
    def add_group(self,company_id,name):
        obj_dup = self.grupo_repository.get_first([Grupo.Nome == name, Grupo.IdEmpresa == company_id])
        if obj_dup:
            raise CustomException((X_ALREADY_EXISTS).format('group'))
        obj = Grupo(company_id,name)
        self.grupo_repository.add(obj)
        return CREATED, 201
    
    def list_group_by_cnpj(self, cnpj, page, per_page):
        response = self.grupo_repository.get_groups_by_cnpj(cnpj, page, per_page)
        print('response', response)
        return jsonify(response)