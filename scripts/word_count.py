import sys

def main():
    # Citim blob-ul binar primit de la pasul anterior din pipeline
    data = sys.stdin.buffer.read()

    # Decodam datele ca text UTF-8 ca sa putem numara cuvintele.
    # errors='ignore' previne crash-ul daca exista bytes non-UTF8 in date.
    text = data.decode('utf-8', errors='ignore')

    # split() imparte textul la spatii si newline-uri, len() numara elementele rezultate
    words = len(text.split())

    # Construim mesajul final si il trimitem pe stdout
    # Acest script este de obicei ultimul pas dintr-un pipeline de analiza text
    result = f"Word count: {words}\n"
    sys.stdout.buffer.write(result.encode('utf-8'))

if __name__ == "__main__":
    main()
