#Repositories
from repositories.repository import Repository
#Tables
from models.schema_elementar import IntegracaoAtualizarNCM
#Libs


class AtualizacaoNcmsRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, IntegracaoAtualizarNCM)