#!/usr/bin/env python3
import sys
import zlib

def main():
    try:
        # Citim datele comprimate venite de la pasul anterior din pipeline
        compressed_data = sys.stdin.buffer.read()

        # Decomprimam datele cu zlib - opusul lui compress.py
        original_data = zlib.decompress(compressed_data)

        # Scriem datele originale pe stdout pentru pasul urmator
        sys.stdout.buffer.write(original_data)

    except Exception as e:
        # Daca datele nu sunt comprimate valid cu zlib, raportam eroarea
        sys.stderr.write(f"Eroare la decompresie: {str(e)}. Fisierul nu este comprimat valid.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
