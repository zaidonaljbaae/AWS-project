class DocumentTypeViewResponse():
    def __init__(self, id, company_id, name, extension, workflow_id):
        self.id = id
        self.company_id = company_id
        self.name = name
        self.extension = extension
        self.workflow_id = workflow_id

    def serialize(self):
        return {c.name: str(getattr(self, c.name))
            for c in self.columns}
