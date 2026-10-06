"""
SELASIH - Selaras dan Kasih Sayang
Prototype dating app mahasiswa (console, interaktif) untuk tugas OOP.

Cara pakai:
    python main.py

Saat dijalankan, program menampilkan tabel user, profil, preferensi, dan jarak.
Setelah itu pengguna memilih User A dan User B (ketik ID atau nama), lalu program
menampilkan hasil MATCH / TIDAK MATCH, persentase kecocokan, dan alasannya.

Perintah di setiap prompt:
    t = tampilkan ulang semua tabel      r = rekomendasi untuk satu user
    m = daftar match yang sudah terjadi  q = keluar
"""

from data import build_demo_engine
from matchmaking import matchmake
from ui import LINE, ask_user, show_result, show_tables


def main():
    engine = build_demo_engine()
    likes = set()
    matches = []

    print(LINE)
    print("   SELASIH  -  Selaras dan Kasih Sayang")
    print("   Prototype Dating App Mahasiswa")
    print(LINE)

    show_tables(engine)

    weights = ", ".join(f"{engine.FACTOR_LABELS[k]} {v * 100:.0f}%" for k, v in engine.weights.items())
    print("\n" + LINE)
    print("  JODOHKAN DUA USER")
    print(LINE)
    print(f"  Bobot skor : {weights}")
    print(f"  Syarat MATCH: kedua user aktif, saling memenuhi preferensi umur & gender,")
    print(f"                dan skor kecocokan >= {engine.match_threshold:.0f}%.")
    print("  Pilih user dengan ID atau nama.")
    print("  Perintah: t = tabel | r = rekomendasi | m = daftar match | q = keluar")

    try:
        while True:
            print()
            user_a = ask_user(engine, matches, "  Pilih User A (ID/nama) : ")
            if user_a is None:
                break
            user_b = ask_user(engine, matches, "  Pilih User B (ID/nama) : ")
            if user_b is None:
                break
            if user_a is user_b:
                print("  User A dan User B harus orang yang berbeda.")
                continue

            result = matchmake(engine, user_a, user_b, likes, matches)
            show_result(engine, result)
    except KeyboardInterrupt:
        print()

    print("\n" + LINE)
    print(f"  Selesai.")
    print(LINE)


if __name__ == "__main__":
    main()
