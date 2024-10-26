import discord
import os
from discord.ext import commands

# Initialiser le bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Créez un événement pour lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f'{bot.user} est connecté !')

# Créez une commande simple
@bot.command()
async def trent(ctx):
    await ctx.send("Je suis à votre écoute grand maître!")

# Lancer le bot avec le token d'environnement
token = os.getenv("DISCORD_TOKEN")
bot.run(token)