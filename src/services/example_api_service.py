from repositories.example_item_repository import ExampleItemRepository

class ExampleApiService:
    def __init__(self, session):
        self.repo = ExampleItemRepository(session)

    def create_item(self, name: str):
        return self.repo.create(name)

    def list_items(self, limit: int = 20):
        return self.repo.list_latest(limit)
