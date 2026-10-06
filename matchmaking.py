from interaction import process_interaction
from match import Match


def find_match(matches, user_a, user_b):
    pair = {user_a.user_id, user_b.user_id}
    for m in matches:
        if {m.user_a.user_id, m.user_b.user_id} == pair:
            return m
    return None


def handle_interaction(interaction, engine, likes, matches):
    """Memproses satu Interaction. Mengembalikan (hasil, match_baru_atau_None)."""
    result = process_interaction(interaction)
    actor, target = interaction.actor, interaction.target

    if result == "LIKE":
        likes.add((actor.user_id, target.user_id))
        sudah_dibalas = (target.user_id, actor.user_id) in likes
        if sudah_dibalas and find_match(matches, actor, target) is None:
            score = engine.calculate_compatibility(target, actor)
            new_match = Match(target, actor, score)   # target = yang Like duluan
            new_match.match()
            matches.append(new_match)
            return result, new_match
    else:
        likes.discard((actor.user_id, target.user_id))
    return result, None


def matchmake(engine, user_a, user_b, likes, matches):
    """Menjodohkan dua user: masing-masing menilai yang lain, Match terbentuk jika sama-sama Like."""
    analysis = engine.explain_compatibility(user_a, user_b)
    decisions = []
    for actor, target in ((user_a, user_b), (user_b, user_a)):
        interaction, reason = engine.decide_interaction(actor, target)
        result, _ = handle_interaction(interaction, engine, likes, matches)
        decisions.append({"actor": actor, "target": target, "result": result, "reason": reason})

    match = find_match(matches, user_a, user_b)
    return {
        "user_a": user_a,
        "user_b": user_b,
        "analysis": analysis,
        "decisions": decisions,
        "match": match,
        "matched": match is not None and match.is_active(),
    }
