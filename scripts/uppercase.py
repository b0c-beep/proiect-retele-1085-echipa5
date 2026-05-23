import sys

def main():
    # Citim datele de intrare in mod binar
    data = sys.stdin.buffer.read()

    # .upper() pe un obiect bytes transforma doar literele ASCII mici in majuscule.
    # Bytes non-ASCII (ex: date comprimate) sunt lasati neatinsi.
    upper_data = data.upper()

    # Scriem rezultatul pe stdout pentru pasul urmator din pipeline
    sys.stdout.buffer.write(upper_data)

if __name__ == "__main__":
    main()
