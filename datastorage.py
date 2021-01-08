import attr
from helper import Vector3
from exceptions import UserNotFound

@attr.s
class User:
    _id = attr.ib()
    username = attr.ib()
    player_position = attr.ib(default=Vector3(0.0, 0.0, 0.0))

    def get_position_asdict(self) -> dict:
        """
            Return position as dict
        """
        return attr.asdict(self.player_position)

    def user_asdict(self) -> dict:
        """
            Return user data as dict
        """
        return attr.asdict(self)


@attr.s
class Users:
    _user_list = []

    def add_new_user(self, user: User):
        self._user_list.append(user)

    def remove_user(self, user: User):
        self._user_list.append(user)

    def get_user(self, username: str) -> User:
        print(f"Searching for user {username}")
        for _user in self._user_list:
            if _user.username == username:
                return _user
        raise UserNotFound("what")


    

