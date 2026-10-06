from utils import _same
from user import User
from interaction import Like, Pass


class MatchingEngine:
    FACTOR_LABELS = {
        "hobby": "Hobi",
        "personality": "Kepribadian",
        "lifestyle": "Gaya hidup",
        "goal": "Tujuan hubungan",
        "distance": "Jarak",
    }
    DEFAULT_WEIGHTS = {
        "hobby": 0.30,
        "personality": 0.25,
        "lifestyle": 0.20,
        "goal": 0.15,
        "distance": 0.10,
    }

    def __init__(self, weights=None, match_threshold=60.0):
        weights = dict(weights or MatchingEngine.DEFAULT_WEIGHTS)
        if set(weights) != set(MatchingEngine.FACTOR_LABELS):
            raise ValueError("Bobot harus mencakup: " + ", ".join(MatchingEngine.FACTOR_LABELS))
        if abs(sum(weights.values()) - 1.0) > 1e-9:
            raise ValueError("Total bobot compatibility harus 1.0 (100%).")
        self.__users = []
        self.__weights = weights
        self.__distances = {}      # {frozenset({id_a, id_b}): km} -> data jarak sederhana
        self.__match_threshold = 0.0
        self.set_match_threshold(match_threshold)

    @property
    def users(self):
        return list(self.__users)

    @property
    def weights(self):
        return dict(self.__weights)

    @property
    def match_threshold(self):
        return self.__match_threshold

    def set_match_threshold(self, value):
        if not 0 <= value <= 100:
            raise ValueError("Ambang match harus di antara 0 dan 100.")
        self.__match_threshold = float(value)

    # ---------- manajemen data ----------
    def add_user(self, user):
        if not isinstance(user, User):
            raise TypeError("Hanya object User yang bisa ditambahkan.")
        if any(u.user_id == user.user_id for u in self.__users):
            raise ValueError(f"User dengan id {user.user_id} sudah terdaftar.")
        self.__users.append(user)

    def set_distance(self, user_a, user_b, km):
        """Jarak disimpan sebagai data sederhana (tanpa GPS)."""
        if km < 0:
            raise ValueError("Jarak tidak boleh negatif.")
        self.__distances[frozenset((user_a.user_id, user_b.user_id))] = float(km)

    def get_distance(self, user_a, user_b):
        return self.__distances.get(frozenset((user_a.user_id, user_b.user_id)))

    # ---------- filter dasar ----------
    def rejection_reason(self, user, candidate):
        """Alasan kenapa `candidate` tidak memenuhi filter dasar `user`; None jika lolos."""
        if user.preference is None:
            raise ValueError(f"{user.name} belum memiliki Preference.")
        if not candidate.is_active():
            return f"{candidate.name} sedang tidak aktif"
        pref = user.preference
        if not pref.is_age_compatible(candidate.age):
            return (f"umur {candidate.name} ({candidate.age} th) di luar rentang yang dicari "
                    f"{user.name} ({pref.min_age}-{pref.max_age} th)")
        if not pref.is_gender_compatible(candidate.gender):
            return (f"{user.name} mencari {pref.preferred_gender}, "
                    f"sedangkan {candidate.name} {candidate.gender}")
        return None

    def find_candidates(self, user):
        """Filter dasar: bukan diri sendiri, aktif, umur sesuai, gender sesuai."""
        if user.preference is None:
            raise ValueError(f"{user.name} belum memiliki Preference.")
        candidates = []
        for candidate in self.__users:
            if candidate is user:
                continue
            if candidate.profile is None or candidate.preference is None:
                continue   # data kandidat belum lengkap, tidak bisa dihitung
            if self.rejection_reason(user, candidate) is not None:
                continue
            candidates.append(candidate)
        return candidates

    # ---------- skor kecocokan ----------
    def calculate_compatibility(self, user_a, user_b):
        """Mengembalikan skor 0 - 100 (float). Hasilnya sama untuk (A, B) maupun (B, A)."""
        return self.explain_compatibility(user_a, user_b)["total"]

    def explain_compatibility(self, user_a, user_b):
        """Skor total beserta rincian tiap faktor dan alasannya."""
        for u in (user_a, user_b):
            if u.profile is None or u.preference is None:
                raise ValueError(f"{u.name} belum memiliki Profile/Preference.")

        calculators = (
            ("hobby", self._calculate_hobby_similarity),
            ("personality", self._calculate_personality_similarity),
            ("lifestyle", self._calculate_lifestyle_similarity),
            ("goal", self._calculate_goal_similarity),
            ("distance", self._calculate_distance_score),
        )
        factors = []
        for key, calculate in calculators:
            score, reason = calculate(user_a, user_b)
            weight = self.__weights[key]
            factors.append({
                "key": key,
                "label": MatchingEngine.FACTOR_LABELS[key],
                "weight": weight,
                "score": score,
                "points": score * weight,
                "reason": reason,
            })
        total = round(sum(f["points"] for f in factors), 2)
        return {"total": total, "factors": factors}

    def generate_recommendations(self, user):
        """Mengembalikan list [(kandidat, skor)] terurut dari skor tertinggi."""
        recommendations = []
        for candidate in self.find_candidates(user):
            score = self.calculate_compatibility(user, candidate)
            recommendations.append((candidate, score))
        recommendations.sort(key=lambda item: item[1], reverse=True)
        return recommendations

    def decide_interaction(self, user, candidate):
        """User menilai candidate -> (Like atau Pass, alasan)."""
        if not user.is_active():
            return Pass(user, candidate), f"{user.name} sedang tidak aktif"

        reason = self.rejection_reason(user, candidate)
        if reason is not None:
            return Pass(user, candidate), reason

        score = self.calculate_compatibility(user, candidate)
        limit = self.__match_threshold
        if score < limit:
            return Pass(user, candidate), f"skor kecocokan {score:.1f}% di bawah ambang {limit:.0f}%"
        return (Like(user, candidate),
                f"{candidate.name} sesuai preferensi {user.name} dan skor {score:.1f}% "
                f"memenuhi ambang {limit:.0f}%")

    # ---------- rumus sederhana tiap faktor: (skor 0-100, alasan) ----------
    def _calculate_hobby_similarity(self, user_a, user_b):
        """Hobi yang sama dibanding jumlah hobi paling sedikit milik salah satu user."""
        hobbies_a, hobbies_b = user_a.profile.hobbies, user_b.profile.hobbies
        common = user_a.profile.has_common_hobby(user_b.profile)
        smallest = min(len(hobbies_a), len(hobbies_b))
        if smallest == 0:
            return 0.0, "Salah satu user belum mengisi hobi."
        score = len(common) / smallest * 100
        if common:
            reason = f"Hobi yang sama: {', '.join(common)} ({len(common)} dari {smallest} hobi)."
        else:
            reason = (f"Tidak ada hobi yang sama ({user_a.name}: {', '.join(hobbies_a)}; "
                      f"{user_b.name}: {', '.join(hobbies_b)}).")
        return score, reason

    def _calculate_personality_similarity(self, user_a, user_b):
        """Sama = 100, melibatkan ambivert = 75, berlawanan = 50."""
        pa, pb = user_a.profile.personality, user_b.profile.personality
        if _same(pa, pb):
            return 100.0, f"Keduanya sama-sama {pa}."
        if _same(pa, "ambivert") or _same(pb, "ambivert"):
            return 75.0, (f"{user_a.name} ({pa}) dan {user_b.name} ({pb}); "
                          "Ambivert mudah menyesuaikan diri.")
        return 50.0, (f"{user_a.name} ({pa}) dan {user_b.name} ({pb}) berbeda sifat, "
                      "kurang searah.")

    def _calculate_lifestyle_similarity(self, user_a, user_b):
        """Dinilai dua arah: keduanya sesuai = 100, satu arah = 70, tidak ada = 40."""
        a_ok = user_a.preference.is_lifestyle_compatible(user_b.profile.lifestyle)
        b_ok = user_b.preference.is_lifestyle_compatible(user_a.profile.lifestyle)

        def clause(seeker, other, ok):
            verb = "sesuai" if ok else "tidak sesuai"
            return (f"{other.name} ({other.profile.lifestyle}) {verb} dengan keinginan "
                    f"{seeker.name} ({seeker.preference.preferred_lifestyle})")

        first, second = clause(user_a, user_b, a_ok), clause(user_b, user_a, b_ok)
        if a_ok and b_ok:
            return 100.0, f"{first}, dan {second}."
        if a_ok or b_ok:
            return 70.0, f"{first}, tetapi {second}."
        return 40.0, f"{first}, dan {second}."

    def _calculate_goal_similarity(self, user_a, user_b):
        """Tujuan hubungan sama = 100, beda = 20."""
        goal_a = user_a.preference.relationship_goal
        goal_b = user_b.preference.relationship_goal
        if user_a.preference.is_goal_compatible(goal_b):
            return 100.0, f"Keduanya mencari hubungan {goal_a}."
        return 20.0, f"Tujuan berbeda: {user_a.name} mencari {goal_a}, {user_b.name} mencari {goal_b}."

    def _calculate_distance_score(self, user_a, user_b):
        """Makin dekat makin tinggi; memakai batas jarak terkecil dari kedua user."""
        distance = self.get_distance(user_a, user_b)
        if distance is None:
            return 50.0, "Data jarak tidak tersedia, dipakai nilai netral."
        limit = min(user_a.preference.max_distance, user_b.preference.max_distance)
        if limit <= 0:
            score = 100.0 if distance == 0 else 0.0
        else:
            score = max(0.0, (1 - distance / limit) * 100)
        note = f"(batas terkecil dari preferensi {user_a.name} dan {user_b.name})"
        if distance > limit:
            return score, f"Jarak {distance:.1f} km melebihi batas {limit:.1f} km {note}."
        return score, f"Jarak {distance:.1f} km dari batas {limit:.1f} km {note}; makin dekat makin tinggi."
