from utils import _same


class Profile:
    def __init__(self, bio, major, semester, hobbies=None, personality="", lifestyle=""):
        # Encapsulation: semua attribute private (double underscore)
        self.__bio = bio
        self.__major = major
        self.__semester = semester
        self.__hobbies = []
        self.__personality = personality
        self.__lifestyle = lifestyle
        for hobby in (hobbies or []):
            self.add_hobby(hobby)

    @property
    def bio(self):
        return self.__bio

    @property
    def major(self):
        return self.__major

    @property
    def semester(self):
        return self.__semester

    @property
    def hobbies(self):
        return list(self.__hobbies)  # salinan, list asli tetap aman

    @property
    def personality(self):
        return self.__personality

    @property
    def lifestyle(self):
        return self.__lifestyle

    def update_bio(self, text):
        self.__bio = text

    def add_hobby(self, hobby):
        hobby = hobby.strip()
        if hobby and not any(_same(hobby, h) for h in self.__hobbies):
            self.__hobbies.append(hobby)

    def remove_hobby(self, hobby):
        for h in self.__hobbies:
            if _same(h, hobby):
                self.__hobbies.remove(h)
                return True
        return False

    def has_common_hobby(self, other_profile):
        """Mengembalikan list hobi yang sama (kosong = tidak ada yang sama)."""
        other = {h.lower() for h in other_profile.hobbies}
        return [h for h in self.__hobbies if h.lower() in other]

    def display(self):
        return {
            "bio": self.__bio,
            "major": self.__major,
            "semester": self.__semester,
            "hobbies": list(self.__hobbies),
            "personality": self.__personality,
            "lifestyle": self.__lifestyle,
        }
