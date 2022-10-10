class User:
    def __init__(self, data):
        self.description = data.get('description')
        self.created_at = data.get('created')
        self.banned = data.get('isBanned')
        self.display = data.get('displayName')
        self.name = data.get('name') if data.get('name') != None else data.get('username')
        self.id = data.get('id') if data.get('id') != None else data.get('userId')