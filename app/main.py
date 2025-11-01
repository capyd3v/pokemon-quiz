from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import random
import requests
import json
from typing import List, Dict
import os

app = FastAPI(title="Pokémon Quiz")

# Configurar directorios
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Crear directorios si no existen
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Cache para Pokémon
pokemon_cache = {}

def get_pokemon_data(pokemon_id: int) -> Dict:
    """Obtiene datos de un Pokémon de la PokeAPI"""
    if pokemon_id in pokemon_cache:
        return pokemon_cache[pokemon_id]
    
    try:
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
        if response.status_code == 200:
            data = response.json()
            pokemon_data = {
                "id": data["id"],
                "name": data["name"],
                "sprite": data["sprites"]["front_default"],
                "types": [t["type"]["name"] for t in data["types"]]
            }
            pokemon_cache[pokemon_id] = pokemon_data
            return pokemon_data
    except Exception as e:
        print(f"Error obteniendo Pokémon {pokemon_id}: {e}")
        return None

def get_random_pokemon() -> Dict:
    """Obtiene un Pokémon aleatorio"""
    pokemon_id = random.randint(1, 151)  # Primera generación (1-151)
    return get_pokemon_data(pokemon_id)

def get_random_options(correct_pokemon: Dict, count: int = 4) -> List[str]:
    """Genera opciones aleatorias incluyendo la respuesta correcta"""
    options = [correct_pokemon["name"]]
    
    while len(options) < count:
        random_id = random.randint(1, 151)
        pokemon = get_pokemon_data(random_id)
        if pokemon and pokemon["name"] not in options:
            options.append(pokemon["name"])
    
    random.shuffle(options)
    return options

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal del quiz"""
    pokemon = get_random_pokemon()
    if not pokemon:
        # Si falla, usar un Pokémon por defecto
        pokemon = {
            "name": "pikachu",
            "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
            "types": ["electric"]
        }
    
    options = get_random_options(pokemon)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pokemon_sprite": pokemon["sprite"],
        "options": options,
        "correct_answer": pokemon["name"],
        "pokemon_types": pokemon["types"]
    })

@app.post("/check-answer")
async def check_answer(selected_name: str = Form(...), correct_answer: str = Form(...)):
    """Verifica si la respuesta es correcta"""
    is_correct = selected_name.lower() == correct_answer.lower()
    return JSONResponse({
        "correct": is_correct,
        "selected_name": selected_name,
        "correct_answer": correct_answer
    })

@app.get("/next-pokemon")
async def next_pokemon():
    """Obtiene un nuevo Pokémon para el quiz"""
    pokemon = get_random_pokemon()
    if not pokemon:
        return JSONResponse({"error": "No se pudo obtener el Pokémon"}, status_code=500)
    
    options = get_random_options(pokemon)
    
    return JSONResponse({
        "sprite": pokemon["sprite"],
        "options": options,
        "correct_answer": pokemon["name"],
        "types": pokemon["types"]
    })

@app.get("/health")
async def health_check():
    """Endpoint para verificar que la app está funcionando"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
