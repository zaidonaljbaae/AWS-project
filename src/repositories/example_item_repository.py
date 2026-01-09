from repositories.repository import Repository
from models.example_item import ExampleItem

class ExampleItemRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, ExampleItem)

    def create(self, name: str) -> ExampleItem:
        item = ExampleItem(name=name)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def list_latest(self, limit: int = 20):
        q = self.session.query(ExampleItem).order_by(ExampleItem.id.desc()).limit(limit)
        return q.all()
