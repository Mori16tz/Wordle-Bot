from sqlalchemy.orm import Session

from database.models import User, UserGuessData


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


def update_user_guess_data(session: Session, data: UserGuessData) -> None:
    """Takes an user object and updates the user in the database."""

    session.merge(data)
