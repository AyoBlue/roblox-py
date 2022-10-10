from .user import User

class Log:
    def __init__(self, data):
        self.data = data
        self.action = data['actionType']
        self.created = data['created']
        for key, var in data['description'].items():
            setattr(self, key.lower(), var)

    @property
    def user(self):
        return User(self.data['actor']['user'])

class SaleEntry:
    def __init__(self, data):
        self.data = data
        self.id = data['id']
        self.created = data['created']
        self.pending = data['isPending']
        self.agent = data['agent']
        self.details = data['details']
        self.currency = data['currency']