import socket
import urllib.parse
import urllib.request
import json

SERVER = "irc.example.com"
PORT = 6667
NICK = "traslatebot"
CHANNEL = "#example"
OWNER = "yournick"

# NickServ: lascia "" per disabilitare l'autenticazione.
NICKSERV_PASSWORD = ""  # Inserisci qui la password NickServ


def traduci_testo(text):
    """Traduce il testo in italiano usando direttamente l'API gratuita di Google Translate"""
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=it&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode('utf-8'))
            tradotto = "".join([item[0] for item in res[0] if item[0]])
            lingua_rilevata = res[2] if len(res) > 2 else "auto"
            return tradotto, lingua_rilevata
    except Exception as err:
        print(f"Errore traduzione: {err}")
        return text, "unknown"


# Connessione compatibile con IPv4 e IPv6
irc = None
ultimo_errore = None

try:
    indirizzi = socket.getaddrinfo(
        SERVER,
        PORT,
        family=socket.AF_UNSPEC,
        type=socket.SOCK_STREAM
    )
except socket.gaierror as e:
    raise SystemExit(f"Impossibile risolvere il server {SERVER}: {e}")

for family, socktype, proto, canonname, sockaddr in indirizzi:
    connessione = socket.socket(family, socktype, proto)

    try:
        print(f"Tentativo di connessione a {sockaddr}...")
        connessione.connect(sockaddr)
        irc = connessione

        if family == socket.AF_INET6:
            print("Connessione effettuata tramite IPv6.")
        else:
            print("Connessione effettuata tramite IPv4.")

        break

    except OSError as e:
        ultimo_errore = e
        print(f"Connessione fallita per {sockaddr}: {e}")
        connessione.close()

if irc is None:
    raise SystemExit(
        f"Impossibile connettersi a {SERVER}:{PORT}. "
        f"Ultimo errore: {ultimo_errore}"
    )


irc.send(f"NICK {NICK}\r\n".encode("utf-8"))
irc.send(f"USER {NICK} 0 * :{NICK}\r\n".encode("utf-8"))

print("Connessione al server IRC in corso.")

buffer = ""
autenticazione_inviata = False
canale_joined = False

while True:
    try:
        dati = irc.recv(2048)

        if not dati:
            print("Connessione IRC chiusa dal server.")
            break

        buffer += dati.decode("utf-8", errors="ignore")
        lines = buffer.split("\r\n")
        buffer = lines.pop()

        for line in lines:

            # Risponde ai ping del server
            if line.startswith("PING"):
                irc.send(
                    f"PONG {line.split()[1]}\r\n".encode("utf-8")
                )
                continue

            # Registrazione completata
            if " 001 " in line:
                print("Connessione IRC completata.")

                # Autenticazione NickServ facoltativa
                if NICKSERV_PASSWORD and not autenticazione_inviata:
                    irc.send(
                        f"PRIVMSG NickServ :IDENTIFY {NICKSERV_PASSWORD}\r\n"
                        .encode("utf-8")
                    )
                    autenticazione_inviata = True
                    print("Comando di autenticazione NickServ inviato.")

                # Entra nel canale dopo la registrazione
                if not canale_joined:
                    irc.send(
                        f"JOIN {CHANNEL}\r\n".encode("utf-8")
                    )
                    canale_joined = True
                    print(f"Richiesto ingresso nel canale {CHANNEL}.")

                continue

            # Segnala eventuali errori di ingresso nel canale
            if any(codice in line for codice in (
                " 403 ", " 405 ", " 471 ", " 473 ",
                " 474 ", " 475 ", " 476 ", " 477 "
            )):
                print(f"Errore IRC relativo al canale: {line}")
                continue

            # Gestione dei messaggi IRC
            if " PRIVMSG " in line:
                # Esempio: :mittente!user@host PRIVMSG #canale :testo
                parts = line.split(" PRIVMSG ", 1)
                sender = parts[0].split("!")[0][1:]

                # Ignora i messaggi scritti dal bot stesso
                if sender.lower() == NICK.lower():
                    continue

                target_and_msg = parts[1].split(" :", 1)
                if len(target_and_msg) < 2:
                    continue

                target = target_and_msg[0].strip()
                text = target_and_msg[1].strip()

                # Traduce soltanto i messaggi del canale configurato
                if target.lower() == CHANNEL.lower() and text:
                    print(f"Messaggio ricevuto da {sender}: {text}")

                    tradotto, lang = traduci_testo(text)

                    risposta = f"[{sender}] ({lang}→it): {tradotto}"
                    irc.send(
                        f"PRIVMSG {OWNER} :{risposta}\r\n".encode("utf-8")
                    )
                    print(f"Query inviata a {OWNER}: {risposta}")

    except KeyboardInterrupt:
        print("Arresto del bot.")
        break

    except Exception as e:
        print("Errore bot:", e)

irc.close()
print("Bot disconnesso.")
