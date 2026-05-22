# Acest modul contine starea globala a serverului.
# Toate celelalte module (handlers, pipeline, cli) importa de aici
# ca sa lucreze pe aceleasi date partajate.

# Clientii conectati in momentul de fata.
# Cheie: ID-ul clientului (ex: "client_1"), Valoare: (reader, writer) pentru socket
clients = {}

# Mapeaza fiecare script la multimea de clienti care il pot rula.
# Ex: { "reverse.py": {"client_1", "client_3"} }
# Un script poate fi tinut de mai multi clienti in acelasi timp.
script_registry = {}

# Pipeline-urile definite de utilizatori.
# Ex: { "flux_meu": ["uppercase.py", "reverse.py"] }
pipelines = {}

# Folosit pentru a sincroniza raspunsurile asincrone in timpul executiei unui pipeline.
# Cand serverul trimite un script la un worker, creeaza un Future si il salveaza aici.
# Cand workerul raspunde, Future-ul este rezolvat si pipeline-ul continua.
# Ex: { "client_1_flux_meu_0": <Future> }
pending_results = {}

# Contor global care creste la fiecare client nou conectat.
# Garanteaza ca fiecare client primeste un ID unic (client_1, client_2 etc.)
client_counter = 0
