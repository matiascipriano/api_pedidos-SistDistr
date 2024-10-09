from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from models.material import Material
from database import SessionLocal
from helpers.logging import logger

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
@router.get("/todos", response_model=None)
def get_materiales_todos(db: Session = Depends(get_db)):
    logger.info("Devolviendo todos los materiales")
    try:
        # Obteniendo todos los centros de recoleccion
        materiales = Material.devolver_materiales_todos(db)
        if (materiales == None):
            raise HTTPException(status_code=404, detail="No se encontraron materiales de recolección en la base de datos.")
        return materiales
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

# Metodo POST para insertar un nuevo material de recoleccion
# POST - /materiales/insertar
@router.post("/insertar", response_model=None)
def insertar_material(nombre: str, descr: str, db: Session = Depends(get_db)):
    
    ## TODO Verificar que el usuario tenga el token necesario

    # Verificando que el material no exista
    materiales = Material.devolver_materiales_todos(db)
    for material in materiales:
        if ((material.nombre).lower() == nombre):
            logger.error(f"El material {nombre} ya existe")
            raise HTTPException(status_code=500, detail=f"Ya existe este material de recolección bajo el nombre: {material.nombre}")
    try:
        # Insertando nuevo material en la db
        logger.info(f"Insertando material: {nombre}")
        material = Material.insertar_material(nombre, db)
        return material
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error insertando nuevo material de recoleccion. {e}")