class Match:
    PENDING = "PENDING"
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"

    def __init__(self, user_a, user_b, compatibility_score):
        if user_a is user_b:
            raise ValueError("Match membutuhkan dua user yang berbeda.")
        self.__user_a = user_a
        self.__user_b = user_b
        self.__compatibility_score = compatibility_score
        self.__status = Match.PENDING

    @property
    def user_a(self):
        return self.__user_a

    @property
    def user_b(self):
        return self.__user_b

    @property
    def compatibility_score(self):
        return self.__compatibility_score

    @property
    def status(self):
        return self.__status

    def match(self):
        """PENDING -> MATCHED"""
        if self.__status != Match.PENDING:
            raise ValueError(f"match() hanya boleh dari PENDING, status sekarang {self.__status}.")
        self.__status = Match.MATCHED

    def unmatch(self):
        """MATCHED -> UNMATCHED"""
        if self.__status != Match.MATCHED:
            raise ValueError(f"unmatch() hanya boleh dari MATCHED, status sekarang {self.__status}.")
        self.__status = Match.UNMATCHED

    def is_active(self):
        return self.__status == Match.MATCHED

    def get_other_user(self, user):
        if user is self.__user_a:
            return self.__user_b
        if user is self.__user_b:
            return self.__user_a
        return None

    def __repr__(self):
        return (f"Match({self.__user_a.name} <-> {self.__user_b.name}, "
                f"score={self.__compatibility_score}, status={self.__status})")
