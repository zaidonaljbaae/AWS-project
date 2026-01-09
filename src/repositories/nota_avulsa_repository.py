#Repositories
from repositories.repository import Repository
#Services
from common.custom_exception import CustomException
from common.error_messages import X_NOT_RECORDS
#Tables
from models.schema_nota_avulsa import *
from models.schema_public import SystemMessage
#Libs
from sqlalchemy import and_, func, extract
from sqlalchemy.sql import text, alias, select
from sqlalchemy_pagination import paginate
import json
from flask import jsonify


class DadosItensRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, DadosItens)

class NotaEntradaRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, NotaEntrada)

class EmpresaRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, EmpresaNotaAvulsa)

    def empresa(self, cnpj):
        return self.session.query(EmpresaNotaAvulsa).\
            filter(EmpresaNotaAvulsa.cpfcnpj.ilike(f'%{cnpj}%')).\
                first()

class AnaliseNotaMessageRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, AnaliseNotaMessage)

    def get_analisys(self, id_nota):
        query = self.session.query(AnaliseNotaMessage.IdNotaEntrada, NotaEntrada.chave, EmpresaNotaAvulsa.cpfcnpj, AnaliseNotaMessage.IdDadosItens,
                                  DadosItens.c_prod.label('CodigoProduto'), DadosItens.x_prod.label('DescricaoProduto'), AnaliseNotaMessage.AliqSugerida, AnaliseNotaMessage.CodMessage, AnaliseNotaMessage.DataCriacao,
                                  AnaliseNotaMessage.Descricao, AnaliseNotaMessage.ValorSugerido, AnaliseNotaMessage.IdNotaEntrada, AnaliseNotaMessage.TypeMessage.label('TipoMensagem'),
                                  SystemMessage.FundLegal, SystemMessage.Link).\
                                    join(DadosItens, DadosItens.id_dados_itens == AnaliseNotaMessage.IdDadosItens, isouter=True).\
                                        filter(and_(AnaliseNotaMessage.IdNotaEntrada == id_nota, SystemMessage.CodMessage == AnaliseNotaMessage.CodMessage,
                                                DadosNota.id_dados_nota == AnaliseNotaMessage.IdNotaEntrada, NotaEntrada.id_dados_nota == DadosNota.id_dados_nota,
                                                EmpresaNotaAvulsa.id == NotaEntrada.empresa_id)).\
                                            all()
        if not query:
            raise CustomException(X_NOT_RECORDS)
        response = []
        for item in query:
            key = [i for i in item._mapping]
            value = [i for i in item._mapping._data]
            obj = dict(zip(key, value))
            response.append(obj)
        return response