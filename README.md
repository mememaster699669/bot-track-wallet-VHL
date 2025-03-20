# 🔍 GAS Wallet Monitor Discord Bot

A personal project Discord bot that tracks and reports real-time **GAS balance updates** for specific NEO wallets (e.g., Upbit, Binance). It periodically fetches balance data via NEO RPC nodes and sends updates to a designated Discord channel.

---

## 📌 Features

- ✅ Monitors GAS balances of selected exchange wallets (Upbit, Binance…)
- 🔁 Sends automatic updates every hour
- 📈 Displays GAS price in USD via CoinGecko API
- 🔔 Sends alerts when balance changes are detected
- 💬 Custom `!gas` command to fetch current balances on demand
- 🤖 Simple spam test command (`!spam yourword`)
- 🌐 Includes a Flask web server for uptime support (Replit/Glitch hosting)

---

## 📁 Project Structure

. ├── main.py # Bot logic ├── .env # Secure token storage (DO NOT COMMIT) ├── .gitignore # Ignores secrets and build files ├── requirements.txt # Required Python packages ├── pyproject.toml # Project metadata (optional) ├── generated-icon.png # Optional bot icon


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repo
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
2️⃣ Install dependencies
pip install -r requirements.txt
3️⃣ Create .env file
At the root of the project, create a file named .env with:

DISCORD_BOT_TOKEN=your_discord_bot_token_here
⚠️ Never commit your .env file!

4️⃣ Run the bot
python main.py
🔐 Environment Variables
Variable	Description
DISCORD_BOT_TOKEN	Your bot's private token (keep secret)
💬 Commands Available
Command	Description
!gas	Displays current balances and USD value
!spam hello	Sends a test spam message (30x repetition)
📡 Technologies Used
Python 3.11+
discord.py
Flask
requests
NEO RPC & CoinGecko API
🤝 Contribution
This is a personal project to explore blockchain wallet monitoring and Discord integration. Feel free to fork or improve it!

👨‍💻 Author
Long – vanhoanglong2002@yahoo.com
