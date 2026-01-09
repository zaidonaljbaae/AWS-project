#Repositories
from repositories.atualizacao_ncm_repository import AtualizacaoNcmsRepository
#Services
from common.default_return_messages import *
#Tables
from models.schema_elementar import IntegracaoAtualizarNCM
#Libs
from flask import jsonify


class AtualizacaoNcmService():

    def __init__(self, db_session):
        self.atualizacao_ncm_repository = AtualizacaoNcmsRepository(db_session)

    def list_table_atualizar_ncm(self, cnpj, page, per_page):
        response = self.atualizacao_ncm_repository.get_all_pagined_and_pop(page, per_page, [IntegracaoAtualizarNCM.CnpjEmpresa == cnpj, IntegracaoAtualizarNCM.Lido == False], ["DataCriacao", "DataAtualizacao", "Ativo", "Excluido", "IdUsuarioAlteracao"])
        return jsonify(response), 200

    def update_table_atualizar_ncm(self, id_register):
        response = self.atualizacao_ncm_repository.get_first([IntegracaoAtualizarNCM.Id == id_register])
        response.Lido = True
        return jsonify(SUCCESS), 200