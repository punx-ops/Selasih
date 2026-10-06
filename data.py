import math

from engine import MatchingEngine
from preference import Preference
from profile import Profile
from user import User


def build_demo_engine():
    """Membuat engine berisi 7 user contoh (data sementara di memory)."""
    data = [
        (1, "Satya", 20, "Laki-laki", "Informatika", 5, "Suka ngoding sambil dengerin musik",
         ["Coding", "Music", "Gaming"], "Introvert", "Active",
         (18, 25, "Perempuan", 10, "Active", "SERIOUS"), (0.0, 0.0)),
        (2, "Bella", 21, "Perempuan", "DKV", 5, "Pecinta fotografi dan game santai",
         ["Music", "Gaming", "Photography"], "Introvert", "Active",
         (19, 25, "Laki-laki", 10, "Active", "SERIOUS"), (2.5, 0.0)),
        (3, "Citra", 20, "Perempuan", "Manajemen", 3, "Anak basket yang hobi jalan-jalan",
         ["Basketball", "Travel"], "Extrovert", "Casual",
         (19, 25, "Laki-laki", 15, "Casual", "CASUAL"), (8.0, 0.0)),
        (4, "Dina", 22, "Perempuan", "Informatika", 7, "Lagi fokus skripsi",
         ["Coding", "Music", "Reading"], "Introvert", "Active",
         (19, 25, "Laki-laki", 10, "Active", "SERIOUS"), (1.0, 0.0)),
        (5, "Rama", 22, "Laki-laki", "Manajemen", 7, "Suka olahraga dan nongkrong",
         ["Basketball", "Travel", "Music"], "Extrovert", "Casual",
         (19, 24, "Perempuan", 15, "Casual", "CASUAL"), (6.0, 5.0)),
        (6, "Bayu", 23, "Laki-laki", "Hukum", 9, "Kutu buku yang suka kopi",
         ["Reading", "Travel", "Photography"], "Ambivert", "Active",
         (20, 26, "Perempuan", 8, "Active", "SERIOUS"), (4.0, 3.0)),
        (7, "Hana", 19, "Perempuan", "Psikologi", 3, "Suka baca dan hunting foto",
         ["Reading", "Photography", "Travel"], "Ambivert", "Active",
         (20, 26, "Laki-laki", 12, "Active", "SERIOUS"), (2.0, 4.0)),
    ]

    engine = MatchingEngine()
    locations = {}
    for (uid, name, age, gender, major, sem, bio, hobbies, personality, lifestyle,
         pref, xy) in data:
        user = User(uid, name, f"{name.lower().replace(' ', '')}@example.com", age, gender)
        user.set_profile(Profile(bio, major, sem, hobbies, personality, lifestyle))
        user.set_preference(Preference(*pref))
        user.activate()
        engine.add_user(user)
        locations[uid] = xy

    users = engine.users
    for i, u in enumerate(users):
        for v in users[i + 1:]:
            (x1, y1), (x2, y2) = locations[u.user_id], locations[v.user_id]
            engine.set_distance(u, v, round(math.hypot(x1 - x2, y1 - y2), 1))

    # Dina menonaktifkan akunnya
    users[3].deactivate()
    return engine
