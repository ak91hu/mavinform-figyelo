# 🚆 MÁV news Discord Bot

![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Python 3.12](https://img.shields.io/badge/Python-3.12-yellow?logo=python)
![Discord Bot](https://img.shields.io/badge/Discord-Bot-7289DA?logo=discord&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red)

A lightweight Python bot that monitors [mavcsoport.hu](https://www.mavcsoport.hu/) and MÁVINFORM pages for new railway news or disruption alerts, then automatically posts them to a Discord channel using a webhook.

---

## ✨ Features

- Monitors multiple MÁV and MÁVINFORM sources:
  - [General news](https://www.mavcsoport.hu/mav-szemelyszallitas/belfoldi-utazas/hirek)
  - [MÁVINFORM feed](https://www.mavcsoport.hu/mavinform)
  - Additional filtered MÁVINFORM pages
- Searches for important keywords
- Sends nicely formatted Discord **embed messages**
- Automatically adds relevant emojis based on the type of issue
- Avoids reposting the same news (keeps track of sent links)
- Fully containerized with **Docker Compose**
- Persistent storage using a bind-mounted `data/` folder
- Configurable check interval (default: every 30 minutes)

---

## 🧩 Project structure

```
mav-news-bot/
├── Dockerfile
├── docker-compose.yml
├── news_to_discord.py
└── data/
    └── sent_links.json
```

---

## ⚙️ Setup and Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/mav-news-discord-bot.git
cd mav-news-discord-bot
```

### 2️⃣ Edit your Discord Webhook
Open `news_to_discord.py` and set:
```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/XXX/YYY"
```

### 3️⃣ Adjust the check interval (optional)
Default is 5 minutes:
```python
CHECK_INTERVAL_SECONDS = 30 * 60
```

You can modify it to any other frequency (in seconds).

---

## 🐳 Docker Setup

### Build and run

```bash
docker compose up -d --build
```

This will:
- Build the Python image from the included `Dockerfile`
- Install required dependencies (`requests`, `beautifulsoup4`)
- Mount the `data/` folder to persist sent links
- Start the bot in the background (`-d`)

### View logs
```bash
docker compose logs -f mav-news-bot
```

### Restart the bot
```bash
docker compose restart mav-news-bot
```

---

## 🧱 File Details

### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY news_to_discord.py .

RUN pip install --no-cache-dir requests beautifulsoup4

VOLUME ["/data"]

CMD ["python", "news_to_discord.py"]
```

### docker-compose.yml
```yaml
services:
  mav-news-bot:
    build: .
    container_name: mav-news-bot
    volumes:
      - ./data:/data
    restart: unless-stopped
```

---

## 🔔 How It Works

1. Every 5 minutes, the bot scrapes MÁV and MÁVINFORM pages.
2. If an article title contains any of the configured keywords:
   - It checks if the URL was already sent.
   - If not, it posts it to your Discord webhook as a rich embed.
3. All processed links are saved in `/data/sent_links.json`, so they won’t be duplicated even after container restarts.

---

## 🧠 Example Discord Message

**Title:**  
> 🚧 MÁV / Traffic Information  

**Body:**  
> Delay between Győr and Hegyeshalom due to a technical failure.  
>  
> 🔗 [Read more on mavcsoport.hu](https://www.mavcsoport.hu/mavinform/example)

**Footer:**  
> Source: MÁVINFORM | MÁV News Watcher

---

## 🛠 Maintenance Commands

| Action | Command |
|--------|----------|
| Restart bot | `docker compose restart mav-news-bot` |
| Stop bot | `docker compose down` |
| Start bot | `docker compose up -d` |
| Rebuild after script changes | `docker compose up -d --build` |
| Check logs | `docker compose logs -f mav-news-bot` |

---

## 📄 License

MIT License © 2025 - You are free to modify and use this code for personal or internal use.

## ❤️ Credits

Created by **Ákos Kovács**, built with a strong dose of *vibe coding energy* ⚡Concept, architecture and documentation crafted together with **ChatGPT (GPT-5)**
