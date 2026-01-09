#Repositorie
from repositories.repository import Repository
#Tables
from models.schema_dlm import *
#Libs
from sqlalchemy import and_, desc
from sqlalchemy_pagination import paginate
import json


class DocumentoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, Documento)

    def get_all_by_type_id(self, page,per_page,document_type_id):
        response = self.session.query(Documento).\
            filter(and_(Documento.Ativo==True,Documento.Excluido==False,Documento.IdTipoDocumento == document_type_id))
        table_paginate = paginate(response, int(page), int(per_page))
        list_columns = []

        for item in table_paginate.items:
            if item.Latest == True:
                tags = self.session.query(Tag).\
                filter(and_(Tag.Id == TagDocumento.IdTag, TagDocumento.Ativo==True, 
                            TagDocumento.Excluido==False, TagDocumento.IdDocumento == item.Id)).all()
                anexos = self.session.query(Documento, DocumentoAnexo.Id).\
                    filter(and_(Documento.Id == DocumentoAnexo.IdAnexo, DocumentoAnexo.IdDocumento == item.Id,
                                DocumentoAnexo.Ativo == True, DocumentoAnexo.Excluido ==False)).all()
                anexados = self.session.query(Documento, DocumentoAnexo.Id).\
                    filter(and_(Documento.Id == DocumentoAnexo.IdDocumento, DocumentoAnexo.IdAnexo == item.Id,
                                DocumentoAnexo.Ativo == True, DocumentoAnexo.Excluido ==False)).all()
                anexos_externos = self.session.query(ArquivoAnexo).\
                    filter(ArquivoAnexo.IdDocumento == item.Id).all()
                object = dict(item.serialize())
                object['tags'] = [tag.serialize() for tag in tags]
                object['versions'] = [version.serialize() for version in table_paginate.items if version.Latest == False and version.Numero == item.Numero]
                
                list_anexos=[]
                for anexo, id_anexo in anexos:
                    obj = anexo.serialize()
                    obj['idAnexo'] = str(id_anexo)
                    list_anexos.append(obj)
                object['anexos'] = list_anexos

                list_anexados=[]
                for anexo, id_anexo in anexados:
                    obj = anexo.serialize()
                    obj['idAnexo'] = str(id_anexo)
                    list_anexados.append(obj)
                object['anexados'] = list_anexados

                anexos_ext=[]
                for anx in anexos_externos:
                    obj = anx.serialize()
                    anexos_ext.append(obj)
                object['anexos_externos'] = anexos_ext
                list_columns.append(object)

        table_paginate.items = list_columns
        return json.dumps(vars(table_paginate))

class TipoDocumentoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, TipoDocumento)

    def get_all_by_cnpj(self, groupId, page=1, per_page=10):
        response = self.session.query(TipoDocumento).\
            filter(and_(TipoDocumento.IdGrupo == groupId))
        table_paginate = paginate(response, int(page), int(per_page))
        list_columns = []

        for item in table_paginate.items:
            list_columns.append(dict(item.serialize()))
            
        table_paginate.items = list_columns
        return vars(table_paginate)

    def get_by_cnpj(self, cnpj, name):
        response = self.session.query(TipoDocumento).\
            filter(and_(TipoDocumento.Nome == name, Empresa.Cnpj == cnpj, TipoDocumento.IdEmpresa == Empresa.Id)).\
                first()
        return vars(response)


class TagDocumentoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, TagDocumento)
        
        
class PalavraChaveRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, PalavraChave)
        
        
class PalavraChaveDocumentoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, PalavraChaveDocumento)
        
        
class DocumentoAnexoRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, DocumentoAnexo)
  
        
class ArquivoAnexoRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, ArquivoAnexo)       ,
        
class GrupoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, Grupo)

    def get_groups_by_cnpj(self, cnpj, page=1, per_page=10):
        response = self.session.query(Grupo).\
            filter(and_(Empresa.Cnpj == cnpj , Grupo.IdEmpresa == Empresa.Id))
        table_paginate = paginate(response, int(page), int(per_page))
        print(table_paginate.items)
        list_columns = []

        for item in table_paginate.items:
            list_columns.append(dict(item.serialize()))
            
        table_paginate.items = list_columns
        return vars(table_paginate)