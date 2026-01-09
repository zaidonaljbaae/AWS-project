#Repositorie
from repositories.repository import Repository
from response_models.document_type_view_response import DocumentTypeViewResponse
#Tables
from models.schema_dlm import *
#Libs
from sqlalchemy import and_, desc
from sqlalchemy_pagination import paginate
import json

class TagRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, Tag)

    def get_all_tags(self, page,per_page,fiters_and=[]):
        response = self.session.query(Tag).\
            filter(and_(*fiters_and))
        table_paginate = paginate(response, int(page), int(per_page))
        list_columns = []

        for item in table_paginate.items:
            avisos = self.session.query(TagAviso).\
            filter(and_(TagAviso.IdTag == item.Id, TagAviso.Ativo==True, TagAviso.Excluido==False)).all()
            object = dict(item.serialize())
            object['avisos'] = [aviso.serialize() for aviso in avisos]
            list_columns.append(object)

        table_paginate.items = list_columns
        return json.dumps(vars(table_paginate))

class TagWorkFlowRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, TagWorkflow)

class TagDocumentoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, TagDocumento)

class TagAvisoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, TagAviso)