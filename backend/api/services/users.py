from schemas.users import User

user_list = [
    User(id=1, name="Rick", surname="Sanchez", email="rick@sanchez.com"),
    User(id=2, name="Morty", surname="Smith", email="morty@smith.com"),
    User(id=3, name="Summer", surname="Smith", email="summer@smith.com")
]

async def list_users(skip: int = 0, limit: int = 10):
    return user_list[skip : skip + limit]

async def get_user(id: int):
    return next((user for user in user_list if user.id == id), None)

async def create_user(user_data: User):
    if any(u.id == user_data.id for u in user_list):
        return None
    user_list.append(user_data)
    return user_data

async def delete_user(id: int):
    user = await get_user(id)
    if user:
        user_list.remove(user)
        return user
    return None

async def update_user(id: int, updated_data: User):
    user = await get_user(id)
    if user:
        user.name = updated_data.name
        user.surname = updated_data.surname
        user.email = updated_data.email
        return user
    return None

