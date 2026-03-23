import discord
from database.guess_data import get_user_guess_data, update_user_guess_data
from database.guess_history import add_new_user_guess, get_user_guess_history
from database.models import User, UserGuessData, Word, WordHistory
from database.user import get_user
from database.word import get_all_words, get_word_history, get_word_today, reset_words
from discord import Client, Embed, Message
from sqlalchemy.orm import Session

from datetime import date

from common.consts import OWNER_ID


def guesses(amount: int, word: str, *, n: bool = True) -> str:
    """Function to generate german formated string."""

    if amount == 1:
        return f"1 {word}"
    if n:
        return f"{amount} {word}en"
    return f"{amount} {word}e"


def generate_emoji_embed(session: Session, user: User, word: Word, word_history: WordHistory) -> Embed:
    """Generate embed with emoji for wordle answer."""

    description = ""
    for history in get_user_guess_history(session, user, word_history):
        guess = history.guess
        emoji_word = ""
        emoji_answer = ""
        marked = list(word.word)
        for i in range(5):
            found = False
            emoji_word += f":regional_indicator_{guess[i]}:"
            if guess[i] == word.word[i]:
                emoji_answer += "🟩"
            else:
                for j in range(5):
                    if guess[i] == word.word[j] and guess[j] != word.word[j] and word.word[j] in marked:
                        emoji_answer += "🟨"
                        found = True
                        marked.remove(word.word[j])
                        break
                if not found:
                    emoji_answer += "🟥"
        description = f"{description}\n{emoji_word}\n{emoji_answer}"
    return Embed(title=user.language.wordle_title, description=description)


async def handle_correct_guess(
    message: Message, user: User, owner: discord.User | None, guess_data: UserGuessData, embed: Embed
) -> None:
    """Function to handle correct user answer."""

    embed.set_footer(text=f"Damit hast du an {guesses(guess_data.streak, "Tag")} in Folge das Wort erraten.")
    await message.reply(embed=embed)
    if owner:
        await owner.send(
            f"{user.username} hat das {user.language.wordle_title} in {guesses(guess_data.guesses, "Versuch")} erraten."
        )


async def handle_incorrect_guess(
    message: Message, user: User, owner: discord.User | None, guess_data: UserGuessData, word: Word, embed: Embed
) -> None:
    """Function to handle incorrect user answer."""

    if guess_data.guesses < 6:
        embed.set_footer(text=f"Du hast noch {guesses(6 - guess_data.guesses, "Versuch", n=False)} übrig.")
    else:
        embed.set_footer(text=f"Das Wort war {word.word}, viel Glück morgen!")
        if owner:
            await owner.send(f"{user.username} hat das {user.language.wordle_title} nicht erraten.")
    await message.reply(embed=embed)


async def analyze_answer(session: Session, message: Message, bot: Client) -> None:
    """Function to handle user answer."""

    reset_words(session)
    user = get_user(session, message.author.id, message.author.name)
    guess = message.content.lower()
    guess_data = get_user_guess_data(session, user)
    word = get_word_today(session, user.language)
    if guess_data.answered:
        await message.reply("Du hast das Wort für heute bereits erraten.")
        return
    if guess_data.guesses == 6:
        await message.reply("Du hattest heute bereits 6 Versuche, das Wort zu erraten.")
        return
    if guess not in get_all_words(session, user.language):
        await message.reply("Dieses Wort ist kein valider Wordle-Guess.")
        return
    guess_data.guesses += 1
    word_history = get_word_history(session, word, date.today())
    add_new_user_guess(session, user, word_history, guess)
    owner = bot.get_user(OWNER_ID)
    embed = generate_emoji_embed(session, user, word, word_history)
    if guess == word.word:
        guess_data.answered = True
        guess_data.streak += 1
        await handle_correct_guess(message, user, owner, guess_data, embed)
    else:
        await handle_incorrect_guess(message, user, owner, guess_data, word, embed)
    update_user_guess_data(session, guess_data)
