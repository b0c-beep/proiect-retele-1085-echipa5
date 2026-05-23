#!/usr/bin/env python3
import sys
import zlib

def main():
    try:
        # Citim tot input-ul binar primit de la pasul anterior din pipeline
        data = sys.stdin.buffer.read()

        # Comprimam datele cu algoritmul zlib la nivelul maxim de compresie (9).
        # Level 9 produce cel mai mic fisier posibil, dar consuma mai mult CPU.
        compressed_data = zlib.compress(data, level=9)

        # Scriem datele comprimate pe stdout pentru pasul urmator
        sys.stdout.buffer.write(compressed_data)

    except Exception as e:
        # Raportam eroarea pe stderr - executorul clientului o va detecta
        # si va opri pipeline-ul cu un mesaj de eroare
        sys.stderr.write(f"Eroare la compresie: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
