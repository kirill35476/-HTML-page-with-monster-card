from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models.models import Monster
from typing import List
from contextlib import asynccontextmanager

# Наша коллекция монстров
monsters_db = {}
monster_counter = 0


# Добавим несколько монстров для примера
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
            name="Феникс",
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
            name="Лесной дух",
            type="природный",
            power=70,
            hp=350,
            is_rare=False,
            image="spirit.png",
            description="Дух леса, защитник природы."
        )
    ]

    for monster in monsters:
        monster_counter += 1
        monster.id = monster_counter
        monsters_db[monster_counter] = monster.model_dump()


# Правильный lifespan с подключением
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Запускаем приложение...")
    init_monsters()
    print(f"📚 Загружено монстров: {len(monsters_db)}")
    yield  # Приложение работает
    # Shutdown
    print("👋 Останавливаем приложение...")


# Передаём lifespan в приложение
app = FastAPI(title="Коллекция монстров", lifespan=lifespan)

# Подключаем папки с шаблонами и статическими файлами
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# 📄 Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с приветствием"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "monsters_count": len(monsters_db)}
    )


# 📄 Эндпоинт для списка всех монстров
@app.get("/monsters", response_class=HTMLResponse)
async def get_monsters_list(request: Request):
    """
    Показывает список всех монстров с ссылками на карточки
    """
    monsters_list = list(monsters_db.values())
    return templates.TemplateResponse(
        "monsters_list.html",
        {"request": request, "monsters": monsters_list}
    )


# 📄 Эндпоинт для отображения карточки монстра
@app.get("/monster/{monster_id}", response_class=HTMLResponse)
async def get_monster_card(request: Request, monster_id: int):
    """
    Показывает красивую HTML страницу с карточкой монстра
    """
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")

    monster = monsters_db[monster_id]
    return templates.TemplateResponse(
        "monster_card.html",
        {"request": request, "monster": monster}
    )


# ============= API эндпоинты (JSON) =============

@app.get("/api/monsters", response_model=List[Monster])
async def get_monsters_api():
    """API для получения всех монстров в JSON"""
    return list(monsters_db.values())


@app.get("/api/monsters/{monster_id}", response_model=Monster)
async def get_monster_api(monster_id: int):
    """API для получения монстра по ID в JSON"""
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")
    return monsters_db[monster_id]


@app.post("/api/monsters", response_model=Monster)
async def create_monster(monster: Monster):
    """API для создания нового монстра"""
    global monster_counter
    monster_counter += 1
    monster.id = monster_counter
    monsters_db[monster_counter] = monster.model_dump()
    return monster


@app.put("/api/monsters/{monster_id}", response_model=Monster)
async def update_monster(monster_id: int, monster: Monster):
    """API для обновления монстра"""
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")

    monster.id = monster_id
    monsters_db[monster_id] = monster.model_dump()
    return monster


@app.delete("/api/monsters/{monster_id}")
async def delete_monster(monster_id: int):
    """API для удаления монстра"""
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")

    del monsters_db[monster_id]
    return {"message": f"Монстр с ID {monster_id} удален"}