users = []


class User:
    global users

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def register_user(self):
        users.append({self.username: self.password})
        print(users)
