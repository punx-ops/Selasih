from utils import _same


class Preference:
    def __init__(self, min_age, max_age, preferred_gender, max_distance,
                 preferred_lifestyle, relationship_goal):
        self.__min_age = 0
        self.__max_age = 0
        self.__max_distance = 0.0
        self.set_age_range(min_age, max_age)      # lewat method -> ikut tervalidasi
        self.set_max_distance(max_distance)
        self.__preferred_gender = preferred_gender
        self.__preferred_lifestyle = preferred_lifestyle
        self.__relationship_goal = relationship_goal

    @property
    def min_age(self):
        return self.__min_age

    @property
    def max_age(self):
        return self.__max_age

    @property
    def preferred_gender(self):
        return self.__preferred_gender

    @property
    def max_distance(self):
        return self.__max_distance

    @property
    def preferred_lifestyle(self):
        return self.__preferred_lifestyle

    @property
    def relationship_goal(self):
        return self.__relationship_goal

    def set_age_range(self, min_age, max_age):
        if min_age < 0 or min_age > max_age:
            raise ValueError("Rentang umur tidak valid: min_age harus >= 0 dan <= max_age.")
        self.__min_age = min_age
        self.__max_age = max_age

    def set_max_distance(self, distance):
        if distance < 0:
            raise ValueError("Jarak maksimum tidak boleh negatif.")
        self.__max_distance = float(distance)

    def is_age_compatible(self, age):
        return self.__min_age <= age <= self.__max_age

    def is_gender_compatible(self, gender):
        return _same(self.__preferred_gender, gender)

    def is_lifestyle_compatible(self, lifestyle):
        return _same(self.__preferred_lifestyle, lifestyle)

    def is_goal_compatible(self, goal):
        return _same(self.__relationship_goal, goal)
