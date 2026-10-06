def _same(a, b):
    """Bandingkan dua string tanpa peduli huruf besar/kecil dan spasi."""
    return str(a).strip().lower() == str(b).strip().lower()
