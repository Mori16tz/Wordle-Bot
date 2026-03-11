from sqlalchemy.orm import Session

from database.database import open_session
from database.models import GuessHistory


def add_new_user_guess(user_id: int, word_history_id: int, guess: str) -> None:
    """Adds an user guess to the database"""

    with open_session() as session:
        session.add(GuessHistory(user_id=user_id, word_history_id=word_history_id, guess=guess))


def get_user_guess_history(session: Session, user_id: int, word_history_id: int) -> list[GuessHistory]:
    """Returns the user guess history for a given word"""

    return (
        session.query(GuessHistory)
        .filter(GuessHistory.user_id == user_id, GuessHistory.word_history_id == word_history_id)
        .all()
    )
