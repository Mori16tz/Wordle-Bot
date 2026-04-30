from sqlalchemy.orm import Session

from database.models import GuessHistory, User, WordHistory


def add_new_user_guess(session: Session, user: User, word_history: WordHistory, guess: str) -> None:
    """Adds an user guess to the database."""

    session.add(GuessHistory(user_id=user.id,
                word_history_id=word_history.id, guess=guess))


def get_user_guess_history(session: Session, user: User, word_history: WordHistory) -> list[GuessHistory]:
    """Returns the user guess history for a given word."""

    return (
        session.query(GuessHistory)
        .filter(GuessHistory.user_id == user.id, GuessHistory.word_history_id == word_history.id)
        .all()
    )
