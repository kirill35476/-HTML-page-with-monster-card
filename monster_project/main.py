from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import asynccontextmanager
import os
import shutil
import uuid


# Модель монстра
class Monster(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    power: int
    hp: int
    is_rare: bool = False
    image: str  # имя файла картинки
    description: Optional[str] = None


# База данных монстров
monsters_db = {}
monster_counter = 0

# Создаем папку для картинок если её нет
os.makedirs("static/images", exist_ok=True)


# Инициализация монстров
def init_monsters():
    global monster_counter
    monsters = [
        Monster(
            name="Огненный дракон",
            type="огненный",
            power=95,
            hp=800,
            is_rare=True,
            image="dragon.png",
            description="Древний дракон, дышащий огнём. Обитает в вулканах и охраняет древние сокровища."
        ),
        Monster(
            name="Искорка",
            type="огненный",
            power=45,
            hp=200,
            is_rare=False,
            image="spark.png",
            description="Маленькая огненная милашка. Очень дружелюбна, но может обжечься."
        ),
        Monster(
            name="Волшебный Феникс",
            type="огненный",
            power=88,
            hp=450,
            is_rare=True,
            image="phoenix.png",
            description="Волшебная птица из магического огня. Возрождается из пепла."
        ),
        Monster(
            name="Ледяной великан",
            type="ледяной",
            power=85,
            hp=600,
            is_rare=True,
            image="giant.png",
            description="Огромный великан из вечных льдов. Обитает в северных горах."
        ),
        Monster(
            name="Снежинка",
            type="ледяной",
            power=30,
            hp=150,
            is_rare=False,
            image="snowflake.png",
            description="Маленькое ледяное создание, приносящее холод."
        ),
        Monster(
            name="Лесной волк",
            type="природный",
            power=75,
            hp=320,
            is_rare=False,
            image="wolf.png",
            description="Благородный лесной волк, защитник древних лесов."
        ),
        Monster(
            name="Лесной дух",
            type="природный",
            power=70,
            hp=350,
            is_rare=False,
            image="spirit.png",
            description="Дух леса, защитник природы."
        ),
        Monster(
            name="Волшебный единорог",
            type="светлый",
            power=82,
            hp=500,
            is_rare=True,
            image="unicorn.png",
            description="Мифическое существо с целебным рогом. Приносит удачу."
        ),
        Monster(
            name="Темный рыцарь",
            type="темный",
            power=90,
            hp=700,
            is_rare=True,
            image="knight.png",
            description="Загадочный рыцарь в черных доспехах. Появляется только в ночное время."
        )
    ]

    for monster in monsters:
        monster_counter += 1
        monster.id = monster_counter
        monsters_db[monster_counter] = monster.model_dump()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запускаем приложение...")
    init_monsters()
    print(f"📚 Загружено монстров: {len(monsters_db)}")
    yield
    print("👋 Останавливаем приложение...")


app = FastAPI(title="Коллекция монстров", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "monsters_count": len(monsters_db)
    })


# Список монстров
@app.get("/monsters", response_class=HTMLResponse)
async def get_monsters_list(request: Request):
    monsters_list = list(monsters_db.values())
    return templates.TemplateResponse("monsters_list.html", {
        "request": request,
        "monsters": monsters_list
    })


# Карточка монстра
@app.get("/monster/{monster_id}", response_class=HTMLResponse)
async def get_monster_card(request: Request, monster_id: int):
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")
    return templates.TemplateResponse("monster_card.html", {
        "request": request,
        "monster": monsters_db[monster_id]
    })


# API: получить всех монстров
@app.get("/api/monsters", response_model=List[Monster])
async def get_monsters_api():
    return list(monsters_db.values())


# API: создать монстра с загрузкой картинки
@app.post("/api/monsters")
async def create_monster(
        name: str = Form(...),
        type: str = Form(...),
        power: int = Form(...),
        hp: int = Form(...),
        is_rare: bool = Form(False),
        description: str = Form(None),
        image: UploadFile = File(None)
):
    global monster_counter

    # Сохраняем картинку
    image_filename = "default.png"
    if image and image.filename:
        ext = image.filename.split('.')[-1]
        image_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = f"static/images/{image_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    monster_counter += 1
    monster = Monster(
        id=monster_counter,
        name=name,
        type=type,
        power=power,
        hp=hp,
        is_rare=is_rare,
        image=image_filename,
        description=description
    )
    monsters_db[monster_counter] = monster.model_dump()
    return monster


# API: обновить монстра и картинку
@app.put("/api/monsters/{monster_id}")
async def update_monster(
        monster_id: int,
        name: str = Form(...),
        type: str = Form(...),
        power: int = Form(...),
        hp: int = Form(...),
        is_rare: bool = Form(False),
        description: str = Form(None),
        image: UploadFile = File(None)
):
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")

    monster = monsters_db[monster_id]

    # Если загружена новая картинка
    if image and image.filename:
        # Удаляем старую картинку
        old_image = monster.get("image")
        if old_image and old_image != "default.png":
            old_path = f"static/images/{old_image}"
            if os.path.exists(old_path):
                os.remove(old_path)

        # Сохраняем новую
        ext = image.filename.split('.')[-1]
        image_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = f"static/images/{image_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        monster["image"] = image_filename

    # Обновляем остальные поля
    monster["name"] = name
    monster["type"] = type
    monster["power"] = power
    monster["hp"] = hp
    monster["is_rare"] = is_rare
    monster["description"] = description

    monsters_db[monster_id] = monster
    return monster


# API: удалить монстра и его картинку
@app.delete("/api/monsters/{monster_id}")
async def delete_monster(monster_id: int):
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")

    monster = monsters_db[monster_id]
    # Удаляем картинку
    if monster.get("image") and monster["image"] != "default.png":
        image_path = f"static/images/{monster['image']}"
        if os.path.exists(image_path):
            os.remove(image_path)

    del monsters_db[monster_id]
    return {"message": f"Монстр с ID {monster_id} удален"}


# HTML форма для загрузки картинки (для удобства)
@app.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})