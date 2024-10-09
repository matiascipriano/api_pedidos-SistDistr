from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from passlib.context import CryptContext
from database import SessionLocal
from helpers.logging import logger
import logging
import asyncio
from routes import materiales, centros, login, usuarios, pedidos
# Crear una instancia de la aplicacion
app = FastAPI()

# Importar las rutas
app.include_router(materiales.router, prefix="/materiales")
app.include_router(centros.router, prefix="/centros")
app.include_router(login.router)
app.include_router(usuarios.router, prefix="/usuarios")
app.include_router(pedidos.router, prefix="/pedidos")

# Icono de la API
favicon_path = 'favicon.ico'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@app.get("/")
async def root():
    return {"message": f"La API que necesitabas para organizar tus pedidos de materiales reciclados."}