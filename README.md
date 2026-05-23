# Motor pentru Execuția de Script-uri la Distanță (Proiect Rețele)

Acest proiect reprezintă o aplicație distribuită client-server ce permite rularea înlănțuită (pipeline) a unor script-uri și executabile aflate pe mașini diferite (clienți conectați / noduri de calcul). Sistemul este agnostic la limbajul de programare, capabil de a procesa date binare (texte, imagini etc.) și vine echipat cu o componentă robustă TCP și o interfață bazată 100% pe terminal (CLI).

## 🚀 Funcționalități Principale
- **Server Concurent (AsyncIO TCP)**: Coordonează execuția distribuind fișiere de la un client la altul în mod non-blocant, folosind un protocol complet binar (Header Length + JSON + Payload).
- **Clienți Interactivi (Shell CLI)**: Oferă flexibilitatea unei console manuale de unde se pot da comenzi direct din terminal pentru a înregistra scripturi și a lansa execuții.
- **Agnostic de Limbaj**: Deoarece comunicarea se face pe bază de `stdin`/`stdout` local, scripturile executate pe nodurile conectate pot fi în absolut orice limbaj (Python, Bash, Node.js, C++ etc.).
- **Toleranță la Erori**: Dacă un client se deconectează brusc, fluxul se întrerupe grațios returnând eroare inițiatorului, iar scripturile deținute de acesta sunt deregistrate automat.

## 🛠 Structura Arhitecturală a Proiectului
* `server/` - Coordonatorul central (Motorul AsyncIO TCP). Păstrează starea rețelei *in-memory*, asignează sarcinile și oferă o consolă interactivă de monitorizare.
* `client/` - Conține shell-ul interactiv `main.py` de unde un nod se poate conecta la rețea și publica funcționalități.
* `scripts/` - Exemple de programe *dummy* (ex: `reverse.py`, `base64_encode.py`, `word_count.py`) ce pot fi executate local de noduri.

---

## 🐳 Rulare folosind Docker (Ghid Complet)

Toate componentele sunt containerizate pentru a rula independent și ușor pe orice sistem.

### 🌟 Rulare automată cu Docker Compose (Recomandat)
Cea mai simplă metodă de a porni întregul cluster (1 Server și 3 Clienți) este folosind fișierul `docker-compose.yml` inclus în proiect.
```bash
docker-compose up -d --build
```
Această comandă ridică infrastructura pe fundal. Pentru a interacționa efectiv cu clienții porniți, trebuie să "te atașezi" de consolele lor, deschizând 3 tab-uri separate de terminal și tastând:

**Tab 1:**
```bash
docker attach motor-cli-node-1
```

**Tab 2:**
```bash
docker attach motor-cli-node-2
```

**Tab 3:**
```bash
docker attach motor-cli-node-3
```

---

### Rulare manuală, pas cu pas (Metoda Alternativă)

**1. Construirea Imaginilor (Build)**
```bash
docker build -t motor-server -f server/Dockerfile .
docker build -t motor-client -f client/Dockerfile .
```

**2. Lansarea Cluster-ului de Calcul**
Pornește serverul principal:
```bash
docker run -d --rm --name motor-server-test -p 8506:8506 motor-server
```

Lansează oricâți clienți dorești în tab-uri separate:
```bash
docker run -it --rm --name cli-node-1 motor-client
```

---

## 💡 Cazuri de Utilizare (Use Cases)

### Use Case 1: Utilizarea Consistentei prin Linie de Comandă (Terminal / CLI)
Aplicația este construită pentru utilizatorii experimentați direct din consolă. Odată intrat în shell-ul clientului (`client>`), ai la dispoziție următoarele comenzi:

**A. Conectarea la rețea**
Comanda `connect <ip> <port>` stabilește conexiunea TCP cu serverul central. (Dacă folosești Docker Compose, scrie `connect server 8506`. Dacă folosești Docker run local, scrie `connect host.docker.internal 8506`).
```text
client> connect server 8506
```

**B. Adăugarea scripturilor locale**
După ce te-ai conectat, comanda `add_script <path>` expune instantaneu un script de pe mașina ta către server, putând fi folosit de oricine din rețea.
```text
client> add_script ./scripts/reverse.py
```

**C. Construirea unui Flux (Pipeline)**
Comanda `publish <nume_pipeline> <script1> <script2> ...` definește pe server o ordine exactă de execuție a scripturilor. Poți combina scripturile tale cu scripturile altor utilizatori deja conectați.
```text
client> publish flux_inversare base64_encode.py reverse.py
```

**D. Generarea Fișierelor de Test (Local)**
Deoarece te afli în interiorul containerului izolat Docker, nu ai acces la fișierele de pe desktopul tău. Din acest motiv, poți genera rapid un fișier pe loc, pe care să îl trimiți mai târziu spre procesare:
```text
client> create_file mesaj.txt Salutari din Docker! Acesta este un test binar.
```

**E. Executarea Fluxului**
Comanda `execute <nume_pipeline> <fisier_intrare>` ia fișierul specificat de pe mașina ta locală, îl trimite prin rețea către server (ca șir de bytes), acesta îl trece prin nodurile corespunzătoare, iar rezultatul se întoarce la tine.
```text
client> execute flux_inversare mesaj.txt
```
*(Rezultatul procesat va fi descărcat instantaneu pe mașina ta sub denumirea `result.out`).*

**Snoop / Interceptare pe Server:**
De fiecare dată când execuți un flux, serverul memorează automat toți pașii intermediari și rezultatul final în folderul intern `/app/output/`. Deoarece am configurat un *Volume Mapping* în Docker Compose, acest folder este sincronizat instantaneu pe PC-ul tău fizic! Vei putea găsi pe desktop, chiar lângă `README.md`, un folder `output` cu absolut toate fișierele generate pas-cu-pas.

### Use Case 2: Procesarea Fișierelor Binare (Imagini, Arhive etc.)
Sistemul comunică prin protocol TCP transferând bytes puri (payload). Nu se limitează la text!
1. Nodul 1 poate expune `compress.py` (comprimă date cu zlib, rezultând trafic de biți)
2. Nodul 2 poate expune `decompress.py` (decomprimă la loc)
Dacă trimiți un fișier oarecare prin `compress.py`, acesta este procesat ca binar de rețea (fără corupere de caractere speciale) și returnat exact așa cum trebuie. Același lucru este valabil și pentru imagini sau audio!

### Use Case 3: Monitorizare în Timp Real (Consola Serverului)
Dacă dorești să vezi exact ce se întâmplă "sub capotă" pe serverul principal și să vizualizezi structurile de date interne, poți deschide serverul în mod interactiv.

1. Dacă folosești Docker Compose, pur și simplu atașează-te la server dintr-un terminal nou:
   ```bash
   docker attach motor-server-node
   ```
2. Imediat vei fi întâmpinat de un prompt `server>`.
3. Tastează comanda `status`. Vei primi pe loc un dump al memoriei interne ce îți arată: câți clienți sunt legați TCP în acea secundă, ce script a adăugat fiecare, și ce fluxuri sunt active.

### Use Case 3: Rezistență la Failures (Fault Tolerance)
Sistemul este robust la pierderea nodurilor.
1. Într-un terminal, apasă `CTRL+C` pe unul din clienții care "dona" scriptul `reverse.py`.
2. Încearcă să rulezi din nou `execute` de pe un alt client conectat.
3. Observă comportamentul rețelei: sistemul nu se prăbușește. Se prinde instant că conexiunea TCP a căzut, returnează o eroare grațioasă inițiatorului (*"Eroare: Clientul tinta s-a deconectat"*), curăță registrul de rețea, iar restul sistemului rămâne 100% funcțional.
