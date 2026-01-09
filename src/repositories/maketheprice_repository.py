#Repositorie
from repositories.repository import Repository
#Tables
from models.schema_maketheprice import *
#Libs
from sqlalchemy import and_, desc


class NotaRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, Nota)
    
    def delete_item(self, item):
        self.session.delete(item)
        self.session.flush()



class EstoqueProdutoRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, EstoqueProduto)



class ProdutoFicha3Repository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, ProdutoFicha3)



class ItemNotaRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, ItemNota)

    def get_item_nota(self, id_cliente, data_inicio, data_final,
                      codigo_produto, session):
        return session.\
        query(ItemNota).\
        join(Nota).\
        filter(and_(Nota.Ativo == True, Nota.Excluido == False,
                    Nota.IdCliente == id_cliente, Nota.DataEmissao.between(data_inicio, data_final),
                    ItemNota.Ativo == True, ItemNota.Excluido == False,
                    ItemNota.CodigoProduto == codigo_produto)).\
        order_by(desc(Nota.DataEmissao)).\
        all()
    
    def delete_itens(self, itens, nota):
        for i in itens:
            self.session.delete(i)
        self.session.flush()
        self.session.delete(nota)



class Ficha3Repository(Repository):

    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, Ficha3)

    def get_ficha3_orderby_desc(self, id_produto_ficha3):
        return self.session.query(Ficha3).\
            filter(and_(Ficha3.Ativo == True, Ficha3.Excluido == False,
            Ficha3.IdProdutoFicha3 == id_produto_ficha3)).\
                order_by(desc(Ficha3.NumOrdem)).\
                    first()