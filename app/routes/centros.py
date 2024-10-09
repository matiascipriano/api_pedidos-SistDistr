from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from models.centro import Centro
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

# Metodo GET para obtener todos los centros existentes en la db
# GET - /centros/todos
@router.get("/todos", response_model=None)
def get_centros_todos(db: Session = Depends(get_db)):
    logger.info("Devolviendo todos los centros")
    try:
        # Obteniendo todos los centros de recoleccion
        centros = Centro.devolver_centros_todos(db)
        if (centros == None):
            raise HTTPException(status_code=404, detail="No se encontraron centros de recolección en la base de datos.")
        return centros
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

# Metodo POST para insertar un nuevo centro de recoleccion
# POST - /centros/insertar
@router.post("/insertar", response_model=None)
def insertar_centro(nombre: str, direcc: str, db: Session = Depends(get_db)):
    
    ## TODO Verificar que el usuario tenga el token necesario

    # Verificando que el centro no exista
    centros = Centro.devolver_centros_todos(db)
    for centro in centros:
        if ((centro.nombre).lower() == nombre):
            logger.error(f"El grupo {nombre} ya existe")
            raise HTTPException(status_code=500, detail=f"Ya existe este centro de recolección bajo el nombre: {centro.nombre}")
    try:
        # Insertando nuevo centro en la db
        logger.info(f"Insertando grupo: {nombre}")
        centro = Centro.insertar_centro(nombre, direcc, db)
        return centro
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error insertando nuevo centro de recoleccion. {e}")