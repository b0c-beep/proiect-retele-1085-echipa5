# Starea globala a clientului, partajata intre toate modulele.
# Folosim un modul separat ca sa evitam importurile circulare
# si ca sa avem un singur loc unde traiesc aceste variabile.

# Scripturile locale pe care acest nod le-a expus in retea.
# Ex: { "reverse.py": "/app/scripts/reverse.py" }
my_scripts = {}

# Obiectele de citire/scriere ale conexiunii TCP cu serverul.
# Sunt None pana cand utilizatorul ruleaza comanda "connect".
reader = None
writer = None
