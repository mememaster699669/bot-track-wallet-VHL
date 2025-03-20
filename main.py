import discord
import os
import requests
import asyncio
from discord.utils import get
import json
from flask import Flask
from threading import Thread

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if TOKEN is None:
    raise ValueError(
        "❌ DISCORD_BOT_TOKEN is not set. Please check your Replit Secrets.")
RPC_URLS = [
    "http://seed1.neo.org:10331", "http://seed2.neo.org:10331",
    "http://seed3.neo.org:10331", "http://seed4.neo.org:10331"
]
GAS_ASSET_HASH = "0xd2a4cff31913016155e38e474a2c06d08be276cf"
wallets = {
    "Upbit": "NhWXj9JfCsF4X6v5ahzHrRH8PQHnrfB8FT",
    "Binance": "NUqLhf1p1vQyP2KJjMcEwmdEBPnbCGouVp",
}

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)
CHANNEL_ID = 1341733499815592107
app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


def get_gas_balance(address):
    payload = {
        "jsonrpc": "2.0",
        "method": "getnep17balances",
        "params": [address],
        "id": 1
    }

    for rpc_url in RPC_URLS:
        try:
            response = requests.post(rpc_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "result" in data:
                balances = data["result"]["balance"]
                gas_balance = 0
                for asset in balances:
                    if asset["assethash"] == GAS_ASSET_HASH:

                        gas_balance = float(asset["amount"]) / (10**8)
                        break
                return gas_balance
            else:
                return f"❌ Error fetching balance: {data.get('error', {}).get('message', 'Unknown error')}"

        except requests.exceptions.SSLError as ssl_err:
            print(f"⚠️ SSL Error with RPC node {rpc_url}: {ssl_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"⚠️ Connection Error with RPC node {rpc_url}: {conn_err}")
        except Exception as e:
            print(f"⚠️ Unexpected Error with RPC node {rpc_url}: {e}")
        continue

    return "❌ All RPC nodes failed."


def get_gas_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=gas&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['gas']['usd']
    except Exception as e:
        return f"❌ Error fetching GAS price: {e}"


async def fetch_gas_balance():
    gas_price = get_gas_price()
    gas_price_display = f"${gas_price:.4f} USD" if not isinstance(
        gas_price, str) else gas_price

    embed = discord.Embed(title="💰 GAS Balances",
                          description=f"📈 **GAS Price:** {gas_price_display}",
                          color=0x00FF00)

    for exchange, address in wallets.items():
        current_balance = get_gas_balance(address)

        change_display = "➖ 0.00 GAS"

        if isinstance(current_balance, str):
            usd_value_display = "N/A"
            from_balance = "N/A"
        else:
            usd_value = current_balance * gas_price if not isinstance(
                gas_price, str) else 0
            usd_value_display = f"~${usd_value:,.2f} USD"

            from_balance = previous_balances.get(exchange, current_balance)

            change = current_balance - from_balance
            if change > 0:
                change_display = f"📈 {change:,.2f} GAS"
            elif change < 0:
                change_display = f"📉 {abs(change):,.2f} GAS"
            else:
                change_display = "➖ 0.00 GAS"

            previous_balances[exchange] = current_balance

        embed.add_field(name=f"**{exchange}**",
                        value=(f"**From:** {from_balance:,.2f} GAS\n"
                               f"**To:** {current_balance:,.2f} GAS\n"
                               f"**Change:** {change_display}\n"
                               f"**USD Value:** {usd_value_display}"),
                        inline=False)

    return embed


previous_balances = {}


async def monitor_transactions():
    await client.wait_until_ready()

    while not client.is_closed():
        channel = client.get_channel(CHANNEL_ID)

        if not isinstance(channel, discord.TextChannel):
            print("❌ Channel is not a TextChannel or is invalid.")
            await asyncio.sleep(180)
            continue

        for exchange, address in wallets.items():
            current_balance = get_gas_balance(address)

            if isinstance(current_balance, str):
                print(
                    f"⚠️ Error fetching balance for {exchange}: {current_balance}"
                )
                continue

            if exchange not in previous_balances:
                previous_balances[exchange] = current_balance
                continue

            if current_balance != previous_balances[exchange]:
                change = current_balance - previous_balances[exchange]

                embed = discord.Embed(
                    title="💰 GAS Balance Update",
                    description=
                    f"📊 **Exchange:** {exchange}\n📅 **Change Detected:**",
                    color=0x00FF00 if change > 0 else 0xFF0000)

                embed.add_field(name="**Asset**", value="GAS", inline=True)
                embed.add_field(
                    name="**From**",
                    value=f"{previous_balances[exchange]:,.2f} GAS",
                    inline=True)
                embed.add_field(name="**To**",
                                value=f"{current_balance:,.2f} GAS",
                                inline=True)

                embed.set_footer(text="⏰ 1hr changes detected")

                try:
                    await channel.send(embed=embed)
                    print(f"✅ Sent transaction alert for {exchange}")
                except Exception as send_error:
                    print(f"❌ Error sending message: {send_error}")

                previous_balances[exchange] = current_balance

        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    await auto_update_gas_balance()
    client.loop.create_task(monitor_transactions())


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!gas'):
        gas_embed = await fetch_gas_balance()
        await message.channel.send(embed=gas_embed)
    if message.content.startswith('!spam'):

        parts = message.content.split(' ', 1)

        if len(parts) < 2 or not parts[1].strip():
            await message.channel.send(
                "⚠️ Please provide a word or phrase to spam. Example: !spam hello"
            )
            return

        phrase_to_spam = parts[1].strip()

        spam_message = ' '.join([phrase_to_spam] * 30)

        await message.channel.send(spam_message)


async def auto_update_gas_balance():
    await client.wait_until_ready()

    channel = client.get_channel(CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        print(
            "❌ Channel not found or is not a TextChannel. Please check the CHANNEL_ID."
        )
        return

    print(f"✅ Auto-updating GAS balance in channel: {channel.name}")

    while not client.is_closed():
        gas_embed = await fetch_gas_balance()
        await channel.send(embed=gas_embed)
        await asyncio.sleep(3600)


keep_alive()

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.start(TOKEN))