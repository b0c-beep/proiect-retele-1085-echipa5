import sys
import base64

def main():
    # Citim datele brute de intrare (pot fi orice tip de fisier)
    data = sys.stdin.buffer.read()

    # Codificam datele binare in format Base64.
    # Base64 transforma orice bytes intr-un sir de caractere ASCII printabile,
    # util pentru a transmite date binare prin canale care suporta doar text.
    encoded_data = base64.b64encode(data)

    # Scriem rezultatul pe stdout pentru pasul urmator din pipeline
    sys.stdout.buffer.write(encoded_data)

if __name__ == "__main__":
    main()
