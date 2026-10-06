# SELASIH — Selaras dan Kasih Sayang

Prototype dating app mahasiswa (console, interaktif) untuk tugas OOP.
Program menampilkan tabel user, lalu pengguna memilih dua user (ID atau nama)
untuk dijodohkan. Hasilnya berupa skor kecocokan 0–100%, status
MATCHED / TIDAK MATCH, rincian per faktor, dan alasan keputusan.

## Struktur file

Satu file per fitur, dijalankan lewat `main.py`:

| File | Isi |
|---|---|
| `main.py` | Entry point, loop CLI (`main()`) |
| `data.py` | `build_demo_engine()` — 7 user contoh di memory |
| `ui.py` | Tampilan console + input (`show_tables`, `show_result`, `ask_user`, …) |
| `matchmaking.py` | `matchmake`, `handle_interaction`, `find_match` |
| `engine.py` | `MatchingEngine` — filter, skor, bobot, ambang |
| `match.py` | `Match` (`PENDING` → `MATCHED` → `UNMATCHED`) |
| `interaction.py` | `Interaction` (ABC), `Like`, `Pass`, `process_interaction` |
| `user.py` | `User` (`ACTIVE` / `INACTIVE`) |
| `profile.py` | `Profile` (bio, prodi, hobi, kepribadian, gaya hidup) |
| `preference.py` | `Preference` (umur, gender, jarak, gaya hidup, tujuan) |
| `utils.py` | `_same` (banding string case-insensitive) |

Impor absolut tanpa titik (`from profile import Profile`); jalankan dari
direktori ini agar impor resolve.

## Syarat

- Python 3 (stdlib saja: `math`, `textwrap`, `abc`), tanpa dependensi eksternal.
- Dijalankan dari direktori project (karena impor absolut antar modul).

## Cara menjalankan

```bash
python3 main.py
```

Non-interaktif (contoh: jodohkan ID 1 dengan ID 2, lalu keluar):

```bash
printf '1\n2\nq\n' | python3 main.py
```

## Cara penggunaan

1. Saat start, program menampilkan 3 tabel: daftar user, profil, preferensi pasangan.
2. Pada prompt `Pilih User A (ID/nama) :` ketik ID (`1`–`7`) atau nama
   (`satya`, `bella`, …), lalu sama untuk User B. Keduanya harus orang berbeda.
3. Program menampilkan `HASIL PERJODOHAN: A <-> B`: skor, grafik bar,
   rincian skor per faktor, penjelasan tiap faktor, penilaian tiap user
   (`LIKE`/`PASS` + alasan), dan baris `HASIL: MATCHED/TIDAK MATCH` beserta alasan.
4. Ulangi untuk pasangan lain, atau keluar dengan `q` / Ctrl+C.

Perintah khusus di setiap prompt (tidak berlaku saat sub-prompt rekomendasi):

| Ketik | Efek |
|---|---|
| `t` / `tabel` | Tampilkan ulang semua tabel |
| `r` / `rekomendasi` | Minta nama/ID user, tampilkan rekomendasi terurut skor + yang terfilter |
| `m` / `match` | Daftar match yang sudah terjadi |
| `q` / `quit` / `exit` / `keluar` | Keluar |

Contoh sesi:

```
Pilih User A (ID/nama) : 1
Pilih User B (ID/nama) : 2
HASIL PERJODOHAN:  Satya  <->  Bella
Skor Kecocokan : 87.5%
HASIL: MATCHED  (87.5%)
```

## Syarat MATCH

Match terbentuk jika **kedua arah** `LIKE`, yaitu tiap user memenuhi semua ini:

- Keduanya `ACTIVE` (catatan: `Dina` mulai sebagai `INACTIVE`).
- Saling memenuhi preferensi umur & gender (bukan skor — filter keras).
- Skor kecocokan ≥ ambang (default 60%).

Skor = rata-rata berbobot: Hobi 30%, Kepribadian 25%, Gaya hidup 20%,
Tujuan hubungan 15%, Jarak 10% (lihat `MatchingEngine.DEFAULT_WEIGHTS`).
Satu `PASS` saja → tidak match; `Match` baru dicatat sekali per pasangan.

## Data demo

`data.py:build_demo_engine()` membuat 7 user: Satya (1), Bella (2), Citra (3),
Dina (4, nonaktif), Rama (5), Bayu (6), Hana (7). Jarak dihitung dari koordinat
kartesius sederhana di memory (km, 1 desimal). Untuk data sendiri, ubah list
`data` di `data.py` mengikuti format tuple yang ada.
