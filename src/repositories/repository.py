#Repositories
#Services
#Tables
#Libs
from sqlalchemy import and_, or_, text
from sqlalchemy_pagination import paginate
from typing import Any, Optional


class Repository():

    def __init__(self, db_session, entity):
        self.session = db_session
        self.entity_type = entity

    def get_first_mf(self, filters=[]):
        return self.session.query(self.entity_type).\
            filter(and_(True,*filters)).\
            first()

    def get_first(self, filters=[]):
        return self.session.query(self.entity_type).\
            filter(and_(self.entity_type.Ativo == True, self.entity_type.Excluido == False)).\
            filter(and_(True,*filters)).\
            first()

    def get_schema_nota_avulsa(self, filters=[]):
        return self.session.query(self.entity_type).\
            filter(and_(True,*filters)).\
            first()

    def get_all(self, filters=[]):
        return self.session.query(self.entity_type).\
            filter(and_(self.entity_type.Ativo == True, self.entity_type.Excluido == False)).\
            filter(and_(True,*filters)).\
            all()

    def get_all_mf(self, filters=[]):
        response = self.session.query(self.entity_type).\
            filter(and_(True,*filters)).\
            all()
        
        response = [i.serialize() for i in response]
        return response

    def get_all_pagined(self, page, per_page, filters_and=[], filters_or: Optional[Any] = []):
        items = self.session.query(self.entity_type).\
            filter(and_(self.entity_type.Ativo == True, self.entity_type.Excluido == False)).\
                filter(and_(True,*filters_and))

        items_paginate = paginate(items, int(page), int(per_page))
        items_json_list = [i.serialize() for i in items_paginate.items]
        items_paginate.items = items_json_list
        return vars(items_paginate)

    def get_all_pagined_and_pop(self, page, per_page, filters_and=[], pop=[], filters_or=[]):
        # ["DataCriacao","DataAtualizacao","Ativo","Excluido","IdUsuarioAlteracao"]
        items = self.session.query(self.entity_type).\
            filter(and_(self.entity_type.Ativo == True, self.entity_type.Excluido == False)).\
            filter(and_(*filters_and)).\
            filter(or_(*filters_or))

        items_paginate = paginate(items, int(page), int(per_page))
        items_json_list = [i.serialize() for i in items_paginate.items]
        removing = [ind.pop(i) for i in pop for ind in items_json_list]
        items_paginate.items = items_json_list
        return vars(items_paginate)

    def add(self, entity):
        self.session.add(entity)
        self.session.flush()

    def add_all(self, entities):
        self.session.add_all(entities)
        self.session.flush()

    def bulk_insert(self, entities):
        self.session.bulk_save_objects(entities)