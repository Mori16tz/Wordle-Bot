from datetime import datetime, time

import discord
from common.algorithm import analyze_answer
from common.consts import TOKEN
from database.database import open_session
from database.models import Language, NotificationState
from database.user import get_user, get_users, reset_users, update_user
from database.word import reset_words
from discord import DMChannel, app_commands
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix="", intents=discord.Intents.all(), help_command=None)


@bot.event
async def on_ready() -> None:
    """Handler that runs once the bot is started. Starts basic loop functions."""

    sync_clock.start()
    await bot.tree.sync()


@bot.event
async def on_message(message: discord.Message) -> None:
    """Handler that runs on each message and checks if it counts as game input."""

    if message.author != bot.user and type(message.channel) is DMChannel:
        with open_session() as session:
            await analyze_answer(session, message, bot)


@bot.tree.command(name="info", description="Erhalte Infos über die Funktionalität des Bots.")
async def info(interaction: discord.Interaction) -> None:
    """Command to get basic information about the bot.:param interaction: The discord interaction."""

    await interaction.response.send_message(
        "Einfach dem Bot eine PN schreiben um zu beginnen.\n"
        "Jede PN wird als Versuch gewertet. Jeder User hat täglich 6 Versuche pro Sprache.\n"
        "Um 0 Uhr werden neue Wörter ausgelost.",
        ephemeral=True,
    )


@bot.tree.command(name="sprachauswahl", description="Ändere die Sprache in der Guesses gewertet werden.")
@app_commands.describe(sprache="Die Sprache vom Wordle.")
async def sprachauswahl(interaction: discord.Interaction, sprache: Language) -> None:
    """Command to change the language per user."""

    with open_session() as session:
        user = get_user(session, interaction.user.id, interaction.user.name)
        user.language = sprache
        update_user(session, user)
        await interaction.response.send_message(f"Die Sprache wurde zu {sprache} geändert.", ephemeral=True)


@bot.tree.command(name="benachrichtigung", description="Ändere die Benachrichtigungseinstellung.")
@app_commands.describe(status="Der Status für die Benachrichtigungen.")
async def benachrichtigung(interaction: discord.Interaction, status: NotificationState) -> None:
    """Command to change the notification state per user."""

    with open_session() as session:
        user = get_user(session, interaction.user.id, interaction.user.name)
        user.notification = status
        update_user(session, user)
        await interaction.response.send_message(f"Benachrichtigungen wurden zu {status} geändert.", ephemeral=True)


@tasks.loop(minutes=1)
async def sync_clock() -> None:
    """Function that syncs the bot time to Berlin timezone."""

    berlin_time = datetime.now().astimezone()
    time_delta = berlin_time.utcoffset()

    dummy_date = datetime.combine(datetime.now(), time(0, 0, 0))
    adjusted_date = dummy_date - time_delta
    adjusted_time = adjusted_date.time()

    daily_loop.change_interval(time=adjusted_time)

    if not daily_loop.is_running():
        daily_loop.start()


@tasks.loop(hours=200000)
async def daily_loop() -> None:
    """Function that runs once each day."""

    reset_words()
    reset_users()
    for user in get_users():
        discord_user = bot.get_user(user.id)
        if discord_user is None or user.notification == NotificationState.Aus:
            continue
        await discord_user.send(
            "Die Wörter wurden geupdatet.\nDiese Benachrichtigung kann mit /benachrichtigung deaktiviert werden."
        )


bot.run(TOKEN)
