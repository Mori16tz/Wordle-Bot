from sqlalchemy.orm import Session

from database.models import User, UserGuessData, Language


def get_user_guess_data(session: Session, user: User) -> UserGuessData:
    """Returns the user guess data for a given user."""

    data = (
        session.query(UserGuessData)
        .filter(UserGuessData.user_id == user.id, UserGuessData.language == user.language)
        .first()
    )
    if data is None:
        new_data = UserGuessData(user_id=user.id, language=user.language)
        session.add(new_data)
        return new_data
    return data


def get_active_users(session: Session, lang: Language) -> list[User]:
    """Returns all Users who already made a guess today"""
    data = (session.query(UserGuessData.user_id).filter(UserGuessData.language== lang, UserGuessData.guesses > 0).all())
    users = []
    for entry in data:
        users.append(session.query(User).filter(User.id==entry.user_id).first())
    return users
        


def update_user_guess_data(session: Session, data: UserGuessData) -> None:
    """Takes an user object and updates the user in the database."""

    session.merge(data)
