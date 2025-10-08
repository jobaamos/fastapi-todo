from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic model for request validation
class Weather(BaseModel):
    city: str
    temperature: int
    description: str

# Fake database (we’ll upgrade to SQLite later)
db = []

@app.get("/")
def read_root():
    return {"message": "Hello, API is working!"}

@app.post("/weather/")
def add_weather(weather: Weather):
    db.append(weather.dict())
    return {"message": "Weather added", "data": weather}

@app.get("/weather/")
def get_weather():
    return {"weather_data": db}
