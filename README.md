# TraslateBot 🌐

**A lightweight IRC translation bot that translates channel messages into Italian.**

TraslateBot is a Python-based IRC bot designed to make multilingual communication easier. It monitors messages in a configured IRC channel, detects the source language automatically, translates messages into Italian, and forwards the translations to a designated IRC user via private message.

## Features

- 🌍 **Automatic language detection** — detects the source language through the translation service.
- 🇮🇹 **Italian translation** — translates incoming channel messages into Italian.
- 💬 **Private delivery** — forwards translated messages to the configured owner.
- 🔌 **IPv4 and IPv6 support** — attempts available server addresses returned by DNS.
- 🔐 **Optional NickServ authentication** — enable it by configuring your NickServ password.
- ⚙️ **Environment-based configuration** — customize the server, nickname, channel, owner, and authentication.
- 🐍 **Python standard library** — no third-party Python packages are required.

## Requirements

- Python 3.9 or newer.
- An IRC account or nickname permitted to connect to your chosen network.
- Network access to the configured IRC server.
- Outbound HTTPS access to Google's translation endpoint.
- Working IPv4 or IPv6 connectivity.

## Installation

### 1. Clone the repository

Replace `YOUR-USERNAME` with your GitHub username.

```bash
git clone https://github.com/YOUR-USERNAME/TraslateBot.git
cd TraslateBot
```

Alternatively, download the repository as a ZIP archive from GitHub and extract it.

### 2. Configure the bot

Copy `.env.example` to `.env`:

**Linux / macOS**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure your IRC settings.

Example:

```dotenv
IRC_SERVER=denver.us.ix.undernet.org
IRC_PORT=6667
IRC_NICK=traslatebot
IRC_CHANNEL=#freeznchosting
IRC_OWNER=bigbastik

NICKSERV_NAME=NickServ
NICKSERV_PASSWORD=
```

**Important:** Python does not automatically load `.env` files. Follow the appropriate instructions below to export the variables before running the bot.

### 3. Run the bot

**Linux / macOS**

```bash
set -a
. ./.env
set +a
python3 bot.py
```

**Windows PowerShell**

```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
        [Environment]::SetEnvironmentVariable(
            $matches[1].Trim(),
            $matches[2].Trim(),
            'Process'
        )
    }
}
python bot.py
```

The bot will connect to the configured IRC server, wait for registration to complete, and then request to join the configured channel.

## Configuration

| Variable | Default value | Description |
|---|---|---|
| `IRC_SERVER` | `denver.us.ix.undernet.org` | IRC server hostname |
| `IRC_PORT` | `6667` | IRC server port |
| `IRC_NICK` | `traslatebot` | Bot nickname |
| `IRC_CHANNEL` | `#freeznchosting` | Channel to monitor |
| `IRC_OWNER` | `bigbastik` | User receiving translated messages |
| `NICKSERV_NAME` | `NickServ` | NickServ service name |
| `NICKSERV_PASSWORD` | Empty | Optional NickServ password |

Change these values to match your IRC network and account.

## Optional NickServ Authentication

NickServ authentication is disabled by default.

To enable it, configure the following variables:

```dotenv
NICKSERV_NAME=NickServ
NICKSERV_PASSWORD=YOUR_NICKSERV_PASSWORD
```

When the IRC server confirms registration, the bot sends an `IDENTIFY` command to NickServ and requests to join the configured channel.

To disable authentication, leave the password empty:

```dotenv
NICKSERV_PASSWORD=
```

The bot does not currently wait for confirmation that authentication succeeded before joining the channel. Networks that require SASL authentication during connection need additional implementation.

### Security recommendations

- Never commit your real NickServ password to GitHub.
- Keep `.env` out of version control.
- If a password has been published, change it immediately.
- Port `6667` is commonly unencrypted. Prefer a TLS-enabled IRC connection when supported by your network.

## IPv4 and IPv6

TraslateBot uses Python's `socket.getaddrinfo()` with `AF_UNSPEC` to retrieve available IPv4 and IPv6 addresses.

It attempts the returned addresses until a connection succeeds or all attempts fail.

IPv6 connectivity depends on your operating system, network, and the IRC server's DNS records. If IPv6 is unavailable, the bot may connect through IPv4 if a usable IPv4 address is returned.

The current implementation does not provide IRC-over-TLS.

## How It Works

1. The bot connects to the configured IRC server.
2. It registers the configured nickname.
3. It optionally sends a NickServ authentication command.
4. It requests to join the configured channel.
5. It listens for messages posted in that channel.
6. It submits each non-empty message to Google's translation endpoint.
7. It sends the translated text to the configured owner through a private IRC message.

Example output:

```text
[ExampleUser] (en→it): Ciao, come stai?
```

The bot ignores messages written by its own nickname to avoid processing its own output.

## Translation Service

TraslateBot uses the following Google Translate endpoint:

```text
https://translate.googleapis.com/translate_a/single
```

This is an unofficial web endpoint, not a guaranteed stable public API. Availability, rate limits, response formats, and access policies may change.

Translation failures are logged to the console. When a translation request fails, the bot returns the original text with the language label `unknown`.

## Privacy

TraslateBot processes messages posted in its configured IRC channel.

Messages are sent to Google's translation endpoint for translation. The resulting translations are then forwarded to the configured owner through a private IRC message.

Before using the bot in a public or private channel:

- Ensure that its operation is permitted by the network and channel rules.
- Inform channel participants where appropriate.
- Avoid processing sensitive or confidential information.
- Configure the destination owner correctly.

The project does not include a web dashboard, database, or persistent message history.

## Troubleshooting

### Connection failed

Check the server hostname, port, DNS resolution, firewall settings, and network connectivity.

### The bot cannot join the channel

Check the IRC error printed in the console. The channel may require a registered account, an invitation, a channel key, or specific privileges.

### NickServ authentication fails

Verify the service name, password, nickname registration, and network requirements. Some IRC networks require SASL instead of post-connection NickServ authentication.

### Translations show `unknown`

Check the console for the translation error. Verify HTTPS connectivity and whether the translation endpoint is available or rate-limited.

### IPv6 does not work

Ensure that IPv6 is enabled and routing is available on the host. The bot can only connect through addresses that the host can reach.

## Project Structure

```text
TraslateBot/
├── bot.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── .github/
    └── ISSUE_TEMPLATE/
        └── bug_report.md
```

## Contributing

Bug reports, suggestions, and improvements are welcome.

When reporting a problem, include the Python version, operating system, IRC network, and relevant error messages. Remove passwords, tokens, and private information from logs before submitting an issue.

## License

This project is distributed under the MIT License. See the `LICENSE` file for details.

## Disclaimer

TraslateBot is an independent community project. It is not affiliated with or endorsed by Google or any IRC network.

The translation endpoint is provided by Google and may be subject to its own terms, restrictions, and availability.
