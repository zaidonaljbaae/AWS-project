#Repositories
from repositories.repository import Repository
#Tables
from models.schema_public import Empresa

class EmpresaRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, Empresa)       
    
    def empresa(self, cnpj):
        return self.session.query(Empresa).\
            filter(Empresa.Cnpj.ilike(f'%{cnpj}%')).\
                first()