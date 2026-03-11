from database.database import open_session
from database.models import GuessHistory

def get_user_guess_history(user_id: int, word_history_id: int):
    with open_session() as session:
        return session.query(GuessHistory).filter(GuessHistory.user_id == user_id, GuessHistory.word_history_id == word_history_id).all()

def add_new_user_guess(session, user, word_history, guess: str):
    session.add(GuessHistory(user_id=user.id, word_history_id=word_history.id, guess=guess))
