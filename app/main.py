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
from fastapi.openapi.utils import get_openapi
# Crear una instancia de la aplicacion
app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Mi API",
        version="1.0.0",
        description="Descripción de mi API con autenticación JWT",
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.1.0"  # Asegurando que estamos usando OpenAPI 3.1.0
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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