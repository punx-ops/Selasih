import textwrap


LINE = "=" * 72


def render_table(headers, rows, aligns=None, indent="  "):
    aligns = aligns or ["<"] * len(headers)
    widths = [max([len(str(h))] + [len(str(r[i])) for r in rows]) for i, h in enumerate(headers)]
    sep = indent + "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt(cells):
        parts = [f" {str(c):{al}{w}} " for c, al, w in zip(cells, aligns, widths)]
        return indent + "|" + "|".join(parts) + "|"

    lines = [sep, fmt(headers), sep] + [fmt(r) for r in rows] + [sep]
    return "\n".join(lines)


def show_table(title, headers, rows, aligns=None):
    print(f"\n  {title}")
    print(render_table(headers, rows, aligns))


def wrap(text, indent=6, width=72):
    """Bungkus teks; untuk bullet ("- ..."), baris lanjutan sejajar dengan isi bullet."""
    extra = 2 if text.startswith("- ") else 0
    return textwrap.fill(text, width=width, initial_indent=" " * indent,
                         subsequent_indent=" " * (indent + extra))


def bar(score, width=20):
    filled = int(round(score / 100 * width))
    return "#" * filled + "." * (width - filled)


def show_tables(engine):
    users = engine.users

    show_table(
        "TABEL 1 - DAFTAR USER",
        ["ID", "Nama", "Umur", "Gender", "Prodi", "Smt", "Status"],
        [[u.user_id, u.name, u.age, u.gender, u.profile.major, u.profile.semester, u.status]
         for u in users],
        ["<", "<", ">", "<", "<", ">", "<"],
    )
    show_table(
        "TABEL 2 - PROFIL",
        ["ID", "Nama", "Hobi", "Kepribadian", "Gaya Hidup"],
        [[u.user_id, u.name, ", ".join(u.profile.hobbies), u.profile.personality,
          u.profile.lifestyle] for u in users],
    )
    show_table(
        "TABEL 3 - PREFERENSI PASANGAN",
        ["ID", "Nama", "Mencari", "Umur", "Jarak Maks", "Gaya Hidup", "Tujuan"],
        [[u.user_id, u.name, u.preference.preferred_gender,
          f"{u.preference.min_age}-{u.preference.max_age}",
          f"{u.preference.max_distance:.0f} km", u.preference.preferred_lifestyle,
          u.preference.relationship_goal] for u in users],
    )


def show_matches(matches):
    if not matches:
        print("\n  Belum ada Match.")
        return
    show_table(
        "DAFTAR MATCH",
        ["No", "Pasangan", "Skor", "Status"],
        [[i, f"{m.user_a.name} <-> {m.user_b.name}", f"{m.compatibility_score:.1f}%", m.status]
         for i, m in enumerate(matches, start=1)],
        [">", "<", ">", "<"],
    )


def show_recommendations(engine, user):
    recommendations = engine.generate_recommendations(user)
    print(f"\n  REKOMENDASI UNTUK {user.name.upper()} (lolos filter umur & gender, urut skor)")
    if recommendations:
        print(render_table(
            ["#", "Nama", "Skor", "Grafik", "Hobi sama"],
            [[i, c.name, f"{s:.1f}%", bar(s, 20),
              ", ".join(user.profile.has_common_hobby(c.profile)) or "-"]
             for i, (c, s) in enumerate(recommendations, start=1)],
            [">", "<", ">", "<", "<"],
        ))
    else:
        print("      (tidak ada kandidat yang lolos filter)")

    rejected = [(u, engine.rejection_reason(user, u)) for u in engine.users if u is not user]
    rejected = [(u, r) for u, r in rejected if r is not None]
    if rejected:
        print("\n  Tidak masuk rekomendasi:")
        for u, reason in rejected:
            print(wrap(f"- {u.name}: {reason}", indent=4))


def verdict_reasons(engine, result):
    """Alasan hasil perjodohan dalam bentuk kalimat."""
    factors = result["analysis"]["factors"]
    score = result["analysis"]["total"]
    limit = engine.match_threshold
    lines = []

    if result["matched"]:
        lines.append("Kedua user lolos syarat umur dan gender yang dicari masing-masing.")
        lines.append(f"Skor kecocokan {score:.1f}% mencapai ambang {limit:.0f}%, "
                     "sehingga keduanya sama-sama memberi Like.")
        strongest = sorted((f for f in factors if f["points"] > 0),
                           key=lambda f: f["points"], reverse=True)[:2]
        if strongest:
            lines.append("Faktor yang paling mendukung: " + ", ".join(
                f"{f['label']} (+{f['points']:.1f} poin)" for f in strongest) + ".")
        return lines

    # kelompokkan alasan Pass yang sama supaya tidak diulang
    grouped = {}
    for d in result["decisions"]:
        if d["result"] == "PASS":
            grouped.setdefault(d["reason"], []).append(d["actor"].name)
    for reason, names in grouped.items():
        who = "Kedua user" if len(names) == 2 else names[0]
        lines.append(f"{who} memberi Pass: {reason}.")

    if any(d["result"] == "LIKE" for d in result["decisions"]):
        liker = next(d["actor"].name for d in result["decisions"] if d["result"] == "LIKE")
        lines.append(f"{liker} memberi Like, tetapi Match baru terbentuk jika kedua user sama-sama Like.")

    if score < limit:
        weakest = sorted(factors, key=lambda f: f["weight"] * 100 - f["points"], reverse=True)
        weakest = [f for f in weakest if f["weight"] * 100 - f["points"] >= 5][:2]
        if weakest:
            lines.append("Faktor yang paling menurunkan skor: " + ", ".join(
                f"{f['label']} (kehilangan {f['weight'] * 100 - f['points']:.1f} poin)"
                for f in weakest) + ".")
    else:
        lines.append(f"Skor kecocokan {score:.1f}% sebenarnya mencapai ambang {limit:.0f}%, "
                     "tetapi syarat preferensi harus terpenuhi lebih dulu.")
    return lines


def show_result(engine, result):
    a, b = result["user_a"], result["user_b"]
    analysis = result["analysis"]
    score = analysis["total"]

    print("\n" + LINE)
    print(f"  HASIL PERJODOHAN:  {a.name}  <->  {b.name}")
    print(LINE)
    print(f"  Skor Kecocokan : {score:.1f}%   [{bar(score)}]")
    print(f"  Ambang MATCH   : {engine.match_threshold:.0f}%")

    rows = [[f["label"], f"{f['weight'] * 100:.0f}%", f"{f['score']:.1f}", f"+{f['points']:.1f}"]
            for f in analysis["factors"]]
    rows.append(["TOTAL", "100%", "", f"{score:.1f}"])
    show_table("RINCIAN SKOR", ["Faktor", "Bobot", "Skor", "Poin"], rows, ["<", ">", ">", ">"])

    print("\n  Penjelasan tiap faktor:")
    for f in analysis["factors"]:
        print(wrap(f"- {f['label']}: {f['reason']}", indent=4))

    print("\n  Penilaian masing-masing user:")
    for d in result["decisions"]:
        print(f"    {d['actor'].name} -> {d['target'].name}: {d['result']}")
        print(wrap(d["reason"], indent=8))

    print("\n" + "-" * 72)
    if result["matched"]:
        print(f"  HASIL: MATCHED  ({score:.1f}%)")
    else:
        print(f"  HASIL: TIDAK MATCH  ({score:.1f}%)")
    print("-" * 72)
    print("  Alasan:")
    for line in verdict_reasons(engine, result):
        print(wrap(f"- {line}", indent=4))


def find_user(engine, text):
    text = text.strip().lower()
    for u in engine.users:
        if text == str(u.user_id) or text == u.name.lower():
            return u
    return None


def ask_user(engine, matches, prompt, commands=True):
    """Meminta user dipilih lewat ID/nama. Mengembalikan None jika keluar/dibatalkan."""
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            return None
        key = raw.lower()

        if key in ("q", "quit", "exit", "keluar"):
            return None
        if commands and key in ("t", "tabel"):
            show_tables(engine)
            continue
        if commands and key in ("m", "match"):
            show_matches(matches)
            continue
        if commands and key in ("r", "rekomendasi"):
            target = ask_user(engine, matches, "  Rekomendasi untuk siapa? (ID/nama) : ",
                              commands=False)
            if target is not None:
                show_recommendations(engine, target)
            continue

        user = find_user(engine, raw)
        if user is not None:
            return user
        print("  User tidak ditemukan. Ketik ID (1-%d) atau nama sesuai Tabel 1." % len(engine.users))
