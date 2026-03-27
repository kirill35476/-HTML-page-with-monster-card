from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import os

# Модель монстра
class Monster(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    power: int
    hp: int
    is_rare: bool = False
    image: str
    description: Optional[str] = None

# База данных монстров
monsters_db = {}
monster_counter = 0

# Создаем папку для картинок
os.makedirs("static/images", exist_ok=True)

# Инициализация монстров
def init_monsters():
    global monster_counter
    monsters = [
        Monster(name="Огненный дракон", type="огненный", power=95, hp=800, is_rare=True, image="images/dragon.png", description="Древний дракон, дышащий огнём."),
        Monster(name="Искорка", type="огненный", power=45, hp=200, is_rare=False, image="🔥", description="Маленькая огненная милашка."),
        Monster(name="Волшебный Феникс", type="огненный", power=88, hp=450, is_rare=True, image="images/phoenix.png", description="Волшебная птица из огня."),
        Monster(name="Ледяной великан", type="ледяной", power=85, hp=600, is_rare=True, image="❄️", description="Огромный великан из льдов."),
        Monster(name="Снежинка", type="ледяной", power=30, hp=150, is_rare=False, image="❄️", description="Маленькое ледяное создание."),
        Monster(name="Лесной волк", type="природный", power=75, hp=320, is_rare=False, image="🐺", description="Благородный лесной волк."),
        Monster(name="Лесной дух", type="природный", power=70, hp=350, is_rare=False, image="🌿", description="Дух леса."),
        Monster(name="Волшебный единорог", type="светлый", power=82, hp=500, is_rare=True, image="🦄", description="Мифическое существо."),
        Monster(name="Темный рыцарь", type="темный", power=90, hp=700, is_rare=True, image="🌑", description="Загадочный рыцарь.")
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
app.mount("/images", StaticFiles(directory="images"), name="images")

# Читаем HTML файл
with open("monster_card.html", "r", encoding="utf-8") as f:
    HTML_CONTENT = f.read()

# Главная страница - отдаем HTML файл
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT

# API: получить всех монстров
@app.get("/api/monsters", response_model=List[Monster])
async def get_monsters_api():
    return list(monsters_db.values())

# API: получить монстра по ID
@app.get("/api/monsters/{monster_id}", response_model=Monster)
async def get_monster_api(monster_id: int):
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")
    return monsters_db[monster_id]

# API: создать монстра
@app.post("/api/monsters")
async def create_monster(monster: Monster):
    global monster_counter
    monster_counter += 1
    monster.id = monster_counter
    monsters_db[monster_counter] = monster.model_dump()
    return monster

# API: обновить монстра
@app.put("/api/monsters/{monster_id}")
async def update_monster(monster_id: int, monster: Monster):
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")
    monster.id = monster_id
    monsters_db[monster_id] = monster.model_dump()
    return monster

# API: удалить монстра
@app.delete("/api/monsters/{monster_id}")
async def delete_monster(monster_id: int):
    if monster_id not in monsters_db:
        raise HTTPException(status_code=404, detail="Монстр не найден")
    del monsters_db[monster_id]
    return {"message": f"Монстр с ID {monster_id} удален"}