from profile import Profile
from preference import Preference


class User:
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    def __init__(self, user_id, name, email, age, gender):
        self.__user_id = user_id
        self.__name = name
        self.__email = email
        self.__age = age
        self.__gender = gender
        self.__status = User.INACTIVE
        self.__profile = None
        self.__preference = None

    @property
    def user_id(self):
        return self.__user_id

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def age(self):
        return self.__age

    @property
    def gender(self):
        return self.__gender

    @property
    def status(self):
        return self.__status

    @property
    def profile(self):
        return self.__profile

    @property
    def preference(self):
        return self.__preference

    # Status hanya boleh berubah lewat method di bawah ini
    def activate(self):
        self.__status = User.ACTIVE

    def deactivate(self):
        self.__status = User.INACTIVE

    def set_profile(self, profile):
        if not isinstance(profile, Profile):
            raise TypeError("profile harus berupa object Profile.")
        self.__profile = profile

    def set_preference(self, preference):
        if not isinstance(preference, Preference):
            raise TypeError("preference harus berupa object Preference.")
        self.__preference = preference

    def is_active(self):
        return self.__status == User.ACTIVE

    def __repr__(self):
        return f"User(id={self.__user_id}, name={self.__name!r}, status={self.__status})"
