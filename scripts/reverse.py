import sys

def main():
    # Citim tot ce vine pe stdin ca date binare
    data = sys.stdin.buffer.read()

    # Slicing-ul [::-1] inverseaza sirul de bytes de la coada la cap.
    # Functioneaza pe orice date binare, nu doar text.
    reversed_data = data[::-1]

    # Scriem rezultatul inversat pe stdout pentru pasul urmator din pipeline
    sys.stdout.buffer.write(reversed_data)

if __name__ == "__main__":
    main()
