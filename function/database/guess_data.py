from database.database import open_session
from database.models import Language, User, UserGuessData


def get_user_guess_data(session, user: User) -> UserGuessData:
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


def update_user_guess_data(session, data: UserGuessData) -> None:
    session.merge(data)
