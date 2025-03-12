from schemas.styles import Style

style_list = [
    Style(id=1, name="Rick", surname="Sanchez", email="rick@sanchez.com"),
    Style(id=2, name="Morty", surname="Smith", email="morty@smith.com"),
    Style(id=3, name="Summer", surname="Smith", email="summer@smith.com")
]

async def list_styles(skip: int = 0, limit: int = 10):
    return style_list[skip : skip + limit]

async def get_style(id: int):
    return next((style for style in style_list if style.id == id), None)

async def create_style(style_data: Style):
    if any(s.id == style_data.id for s in style_list):
        return None
    style_list.append(style_data)
    return style_data

async def delete_style(id: int):
    style = await get_style(id)
    if style:
        style_list.remove(style)
        return style
    return None

async def update_style(id: int, updated_data: Style):
    style = await get_style(id)
    if style:
        style.name = updated_data.name
        style.description = updated_data.description
        style.image = updated_data.image
        return style
    return None