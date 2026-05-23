import sys
import base64

def main():
    # Citim datele codificate Base64 de pe stdin
    data = sys.stdin.buffer.read()

    try:
        # Decodificam din Base64 inapoi in forma binara originala
        decoded_data = base64.b64decode(data)

        # Scriem rezultatul pe stdout pentru pasul urmator din pipeline
        sys.stdout.buffer.write(decoded_data)
    except Exception:
        # Daca sirul primit nu este Base64 valid, semnalam eroarea
        sys.stdout.buffer.write(b'ERROR_DECODING_BASE64')

if __name__ == "__main__":
    main()
