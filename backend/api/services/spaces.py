from schemas.spaces import Space

space_list = [
    Space(id=1, name="Rick", surname="Sanchez", email="rick@sanchez.com"),
    Space(id=2, name="Morty", surname="Smith", email="morty@smith.com"),
    Space(id=3, name="Summer", surname="Smith", email="summer@smith.com")
]

async def list_spaces(skip: int = 0, limit: int = 10):
    return space_list[skip : skip + limit]

async def get_space(id: int):
    return next((space for space in space_list if space.id == id), None)

async def create_space(space_data: Space):
    if any(s.id == space_data.id for s in space_list):
        return None
    space_list.append(space_data)
    return space_data

async def delete_space(id: int):
    space = await get_space(id)
    if space:
        space_list.remove(space)
        return space
    return None

async def update_space(id: int, updated_data: Space):
    space = await get_space(id)
    if space:
        space.name = updated_data.name
        space.description = updated_data.description
        space.image = updated_data.image
        return space
    return None