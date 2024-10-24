from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from models.material import Material
from database import SessionLocal
from helpers.logging import logger
from routes import login

# Tener una session nueva para cada consulta
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

router = APIRouter()

# Metodo GET para obtener todos los materiales existentes en la db
# GET - /materiales/todos
@router.get("/todos", response_model=None, tags=["admin"])
def get_materiales_todos(db: Session = Depends(get_db)):
    logger.info("Devolviendo todos los materiales")
    try:
        # Obteniendo todos los centros de recoleccion
        materiales = Material.devolver_materiales_todos(db)
        if not materiales:
            logger.error(f"No hay materiales")
            raise Exception(f"No se encontraron materiales de recolección en la base de datos.")
        return materiales
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")

# Metodo POST para insertar un nuevo material de recoleccion
# POST - /materiales/insertar
@router.post("/insertar", response_model=None, tags=["admin"])
def insertar_material(nombre: str, request: Request, descr: str, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Verificando que el material no exista
        if (Material.devolver_material_por_nombre(nombre,db)):
            logger.error(f"El material {nombre} ya existe")
            raise Exception(f"Ya existe este material de recolección bajo el nombre: {nombre}")
    
        # Insertando nuevo material en la db
        logger.info(f"Insertando material: {nombre}")
        material = Material.insertar_material(nombre,descr, db)
        return material
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error insertando nuevo material de recoleccion. {e}")