from sqlalchemy.orm import Session

from database.models import User


def get_user(session: Session, user_id: int, username: str) -> User | None:
    """Returns an user object for a given id. If none exists, an user is created."""

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        session.add(User(id=user_id, username=username))
        user = session.query(User).filter(User.id == user_id).first()
    return user


def get_users(session: Session) -> list[User]:
    """Returns all users saved in the database."""

    return session.query(User).all()


def update_user(session: Session, user: User) -> None:
    """Takes an user object and updates this user in the database."""

    session.merge(user)


def reset_users(session: Session) -> None:
    """Resets the users guesses and updates their streak."""

    users = session.query(User).all()
    for user in users:
        for guess_data in user.user_guess_data:
            guess_data.guesses = 0
            if not guess_data.answered:
                guess_data.streak = 0
            guess_data.answered = False
        session.merge(user)
