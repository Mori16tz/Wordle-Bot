from sqlalchemy.orm import Session

from database.models import User


def get_user(session: Session, user_id: int, username: str) -> User | None:
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        session.add(User(id=user_id, username=username))
        user = session.query(User).filter(User.id == user_id).first()
    return user


def get_users(session: Session) -> list[User]:
    return session.query(User).all()


def update_user(session: Session, user: User) -> None:
    session.merge(user)


def reset_users(session: Session) -> None:
    users = session.query(User).all()
    for user in users:
        for guess_data in user.user_guess_data:
            guess_data.guesses = 0
            if not guess_data.answered:
                guess_data.streak = 0
            guess_data.answered = False
        session.merge(user)
