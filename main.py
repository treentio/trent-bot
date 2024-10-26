import discord
import os
import random
import json
import asyncio
from discord.ext import commands

# Initialisation du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Fichier de sauvegarde des données utilisateurs
DATA_FILE = "users_data.json"

# Charger les données des utilisateurs depuis le fichier JSON
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Sauvegarder les données des utilisateurs dans le fichier JSON
def save_user_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users_data, f)

# Charger les données utilisateurs
users_data = load_user_data()

# Équipement slots de base
slots_equipement = {
    "Casque": None,
    "Jambière": None,
    "Torse": None,
    "Chaussures": None,
    "Bouclier": None,
    "Épaulière": None,
    "Avant-Bras": None,
    "Arme": None,
    "Artefact": None  # Ajout d'un slot pour les artefacts
}

# Fonction pour récupérer ou initialiser les données d'un utilisateur
def get_user_data(user_id):
    if str(user_id) not in users_data:
        users_data[str(user_id)] = {
            "nom": None,
            "prenom": None,
            "age": None,
            "sexe": None,
            "classe": None,
            "niveau": 1,
            "points_a_investir": 0,
            "puissance": 0,
            "agilite": 0,
            "dexterite": 0,
            "magie": 0,
            "endurance": 0,
            "inventaire": {},
            "equipement": slots_equipement.copy(),
            "historique_combat": []
        }
        save_user_data()  # Sauvegarde les nouvelles données
    return users_data[str(user_id)]

# Commande pour afficher l'inventaire
@bot.command()
async def inventaire(ctx):
    user_data = get_user_data(ctx.author.id)
    embed = discord.Embed(
        title=f"📦 Inventaire de **{ctx.author.name}**",
        description="Voici ce que vous avez dans votre inventaire :",
        color=discord.Color.green()
    )

    # Afficher les équipements équipés
    embed.add_field(name="🛡️ Équipements équipés :", 
                    value="\n".join([f"**{slot}:** {item if item else '🛑 Aucun'}" for slot, item in user_data["equipement"].items()]), 
                    inline=False)

    # Afficher l'inventaire
    if user_data["inventaire"]:
        embed.add_field(name="🔍 Contenu de l'inventaire :", 
                        value="\n".join([f"**{item}:** {quantity}" for item, quantity in user_data["inventaire"].items()]), 
                        inline=False)
    else:
        embed.add_field(name="🔍 Contenu de l'inventaire :", value="Votre inventaire est vide. 🗃️", inline=False)

    await ctx.send(embed=embed)

# Commande pour commencer l'aventure
@bot.command()
async def commencer(ctx, nom: str, prenom: str, age: int, sexe: str, classe: str):
    user_data = get_user_data(ctx.author.id)

    # Initialiser les données du joueur
    user_data["nom"] = nom
    user_data["prenom"] = prenom
    user_data["age"] = age
    user_data["sexe"] = sexe
    user_data["classe"] = classe

    save_user_data()  # Sauvegarde les modifications

    await ctx.send(f"{ctx.author.mention}, votre profil a été créé avec succès ! Utilisez `!profil` pour voir vos informations.")

# Commande pour afficher le profil d'un utilisateur
@bot.command()
async def profil(ctx):
    user_data = get_user_data(ctx.author.id)

    # Initialisation de la page
    page = 1

    embed = discord.Embed(
        title=f"🎮 Profil de **{ctx.author.name}**",
        color=discord.Color.blue()
    )

    # Création de l'embed pour la première page
    embed.description = "**Informations personnelles :**"
    embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.add_field(name="Nom", value=user_data["nom"], inline=True)
    embed.add_field(name="Prénom", value=user_data["prenom"], inline=True)
    embed.add_field(name="Âge", value=user_data["age"], inline=True)
    embed.add_field(name="Sexe", value=user_data["sexe"], inline=True)
    embed.add_field(name="Classe de combat", value=user_data["classe"], inline=True)
    embed.add_field(name="💼 Niveau", value=user_data["niveau"], inline=True)

    # Envoie l'embed initial et ajoute la réaction pour la navigation
    message = await ctx.send(embed=embed)
    await message.add_reaction("➡️")  # Page suivante

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["➡️", "⬅️", "⚔️", "🌀", "🎯", "🔮", "💪"]

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "➡️" and page == 1:
                page = 2  # Va à la page 2
                # Met à jour l'embed pour la deuxième page
                embed.description = "**Détails des stats :**"
                embed.clear_fields()  # Effacer les champs précédents
                embed.add_field(name="✨ Points à investir", value=user_data["points_a_investir"], inline=True)
                embed.add_field(name="⚔️ Puissance", value=user_data["puissance"], inline=True)
                embed.add_field(name="🌀 Agilité", value=user_data["agilite"], inline=True)
                embed.add_field(name="🎯 Dextérité", value=user_data["dexterite"], inline=True)
                embed.add_field(name="🔮 Magie", value=user_data["magie"], inline=True)
                embed.add_field(name="💪 Endurance", value=user_data["endurance"], inline=True)

                await message.edit(embed=embed)  # Met à jour le même embed
                await message.clear_reactions()  # Supprime les anciennes réactions
                await message.add_reaction("⬅️")  # Retour à la page 1
                await message.add_reaction("⚔️")  # Investir dans puissance
                await message.add_reaction("🌀")  # Investir dans agilité
                await message.add_reaction("🎯")  # Investir dans dextérité
                await message.add_reaction("🔮")  # Investir dans magie
                await message.add_reaction("💪")  # Investir dans endurance

            elif str(reaction.emoji) == "⬅️" and page == 2:
                page = 1  # Retourne à la page 1
                # Met à jour l'embed pour la première page
                embed.description = "**Informations personnelles :**"
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.clear_fields()  # Effacer les champs précédents
                embed.add_field(name="Nom", value=user_data["nom"], inline=True)
                embed.add_field(name="Prénom", value=user_data["prenom"], inline=True)
                embed.add_field(name="Âge", value=user_data["age"], inline=True)
                embed.add_field(name="Sexe", value=user_data["sexe"], inline=True)
                embed.add_field(name="Classe de combat", value=user_data["classe"], inline=True)
                embed.add_field(name="💼 Niveau", value=user_data["niveau"], inline=True)

                await message.edit(embed=embed)  # Met à jour le même embed
                await message.clear_reactions()  # Supprime les anciennes réactions
                await message.add_reaction("➡️")  # Page suivante

            # Supprimer la réaction de l'utilisateur
            await message.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            await message.clear_reactions()  # Supprimer les réactions après le délai
            break

        # Gestion des investissements de points
        if page == 2:
            if str(reaction.emoji) == "⚔️" and user_data["points_a_investir"] > 0:  # Investir dans puissance
                user_data["puissance"] += 1
                user_data["points_a_investir"] -= 1
                await ctx.send(f"{ctx.author.mention}, vous avez investi un point dans la puissance !")
                save_user_data()

            elif str(reaction.emoji) == "🌀" and user_data["points_a_investir"] > 0:  # Investir dans agilité
                user_data["agilite"] += 1
                user_data["points_a_investir"] -= 1
                await ctx.send(f"{ctx.author.mention}, vous avez investi un point dans l'agilité !")
                save_user_data()

            elif str(reaction.emoji) == "🎯" and user_data["points_a_investir"] > 0:  # Investir dans dextérité
                user_data["dexterite"] += 1
                user_data["points_a_investir"] -= 1
                await ctx.send(f"{ctx.author.mention}, vous avez investi un point dans la dextérité !")
                save_user_data()

            elif str(reaction.emoji) == "🔮" and user_data["points_a_investir"] > 0:  # Investir dans magie
                user_data["magie"] += 1
                user_data["points_a_investir"] -= 1
                await ctx.send(f"{ctx.author.mention}, vous avez investi un point dans la magie !")
                save_user_data()

            elif str(reaction.emoji) == "💪" and user_data["points_a_investir"] > 0:  # Investir dans endurance
                user_data["endurance"] += 1
                user_data["points_a_investir"] -= 1
                await ctx.send(f"{ctx.author.mention}, vous avez investi un point dans l'endurance !")
                save_user_data()

# Commande pour commencer le combat
@bot.command()
async def combat(ctx):
    monstres = ["Squelette", "Loup", "Goblin"]
    monstre = random.choice(monstres)

    # Création de l'embed pour le combat
    embed = discord.Embed(
        title=f"⚔️ Combat contre **un {monstre}**!",
        description="🔔 Appuyez sur ✅ pour commencer le combat.",
        color=discord.Color.red()
    )

    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")  # Réaction pour commencer le combat

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "✅"

    try:
        # Attendre la réaction de l'utilisateur
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)

        # Démarrer le combat
        await message.clear_reactions()  # Retirer la réaction de départ
        await message.edit(content=f"⚔️ Vous combattez **un {monstre}**!", embed=None)

        # Statistiques du monstre
        monstre_pv = random.randint(5, 10)
        monstre_attaque = random.randint(1, 5)

        # Boucle de combat
        while monstre_pv > 0:
            await ctx.send(f"💖 Vous avez **{monstre_pv} PV** restant.")
            await ctx.send("Choisissez votre action :\n1. Attaquer\n2. Défendre")

            def action_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content in ["1", "2"]

            try:
                action_msg = await bot.wait_for("message", timeout=30.0, check=action_check)

                if action_msg.content == "1":  # Attaque
                    degats = random.randint(1, 5) + users_data[str(ctx.author.id)]["puissance"]  # Ajouter la puissance
                    monstre_pv -= degats
                    await ctx.send(f"✨ Vous avez infligé **{degats} dégâts** au {monstre}!")

                elif action_msg.content == "2":  # Défense
                    def_attaque = monstre_attaque // 2
                    await ctx.send(f"🛡️ Vous défendez! Dégâts réduits à **{def_attaque}**.")
                    monstre_pv -= 0  # Aucun dégât au monstre pendant la défense

                # Monstre attaque
                if monstre_pv > 0:
                    if action_msg.content == "2":  # Si le joueur défend
                        await ctx.send(f"😱 Le {monstre} attaque et vous inflige **{def_attaque} dégâts**!")
                    else:
                        await ctx.send(f"😨 Le {monstre} attaque et vous inflige **{monstre_attaque} dégâts**!")

                # Gérer la fin du combat
                if monstre_pv <= 0:
                    await ctx.send(f"🎉 Vous avez vaincu **le {monstre}**!")
                    users_data[str(ctx.author.id)]["points_a_investir"] += 1  # Récompense
                    await ctx.send(f"💰 Vous gagnez **1 point à investir**! Total: {users_data[str(ctx.author.id)]['points_a_investir']}")

            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé! Vous avez perdu le tour.")
                continue

    except asyncio.TimeoutError:
        await ctx.send("🚫 Vous n'avez pas réagi à temps et le combat est annulé.")

    save_user_data()  # Sauvegarder les données après le combat

# Démarrage du bot
bot.run(os.getenv("DISCORD_TOKEN"))