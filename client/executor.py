import subprocess

async def execute_local_script(script_path: str, payload: bytes) -> tuple[bool, bytes, str]:
    # Ruleaza un script local ca subproces separat si returneaza rezultatul.
    # Datele de intrare (payload) sunt trimise pe stdin-ul scriptului,
    # iar rezultatul este citit de pe stdout-ul lui.
    # Aceasta abordare permite rularea oricarui executabil (Python, Bash, C++ etc.)
    # atata timp cat acesta stie sa citeasca stdin si sa scrie stdout.
    #
    # Returneaza: (succes, date_output, mesaj_eroare)
    try:
        # Fisierele .py sunt rulate explicit cu interpretorul Python.
        # Orice alt fisier este tratat ca executabil direct (ex: binar compilat).
        cmd = ["python", script_path] if script_path.endswith('.py') else [script_path]

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,   # trimitem date pe stdin
            stdout=subprocess.PIPE,  # citim rezultatul de pe stdout
            stderr=subprocess.PIPE   # capturam erorile separat
        )

        # communicate() injecteaza payload-ul pe stdin si asteapta terminarea procesului.
        # Timeout-ul de 25 secunde protejeaza workerul de scripturi blocate la infinit.
        stdout_data, stderr_data = proc.communicate(input=payload, timeout=25)

        # Return code 0 inseamna succes in conventiile POSIX si Windows
        if proc.returncode == 0:
            return True, stdout_data, ""
        else:
            # Scriptul a esuat - citim mesajul de eroare de pe stderr
            err = stderr_data.decode('utf-8', errors='replace')
            return False, b'', f"Exit code {proc.returncode}: {err}"

    except subprocess.TimeoutExpired:
        # Scriptul a depasit limita de timp - il oprim fortat
        proc.kill()
        return False, b'', "Timeout executie script."
    except Exception as e:
        # Orice alta eroare de sistem (ex: fisierul scriptului nu a fost gasit)
        return False, b'', str(e)
