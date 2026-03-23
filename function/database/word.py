import random
from datetime import date

from sqlalchemy.orm import Session

from database.models import Language, Word, WordHistory


def generate_word_today(session: Session, language: Language) -> str:
    """Function to generate a word in a given language for today."""

    potential_words = session.query(Word).filter(Word.language == language, Word.potential_answer).all()
    random_word = random.choice(potential_words)  # noqa: S311
    new_word_history = WordHistory(word_id=random_word.id, date=date.today())
    session.add(new_word_history)
    return random_word.word


def get_word_today(session: Session, language: Language) -> Word:
    """Returns the word for today in the given language."""

    word_entry = (
        session.query(WordHistory)
        .join(Word)
        .filter(Word.language == language, WordHistory.date == date.today())
        .first()
    )
    if word_entry is None:
        raise ValueError
    return word_entry.word


def get_all_words(session: Session, language: Language) -> list[str]:
    """Returns all words in a given Language."""

    return [word.word for word in session.query(Word).filter(Word.language == language).all()]


def get_word_history(session: Session, word: Word, word_date: date) -> WordHistory:  # noqa: B008
    """Returns the word history for a given word and date, date defaults to today."""

    return session.query(WordHistory).filter(WordHistory.word_id == word.id, WordHistory.date == word_date).first()


def reset_words(session: Session) -> None:
    """Resets the words. If no word for today exists, a new one is generated."""

    for language in Language:
        try:
            get_word_today(session, language)
        except ValueError:
            generate_word_today(session, language)
