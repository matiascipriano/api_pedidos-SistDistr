from routes import login
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from models.pedido import Pedido
from database import SessionLocal
from helpers.logging import logger
from pydantic import BaseModel

# Tener una session nueva para cada consulta
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

router = APIRouter()

class PedidoDB(BaseModel):
    estado : str
    cliente : str
    # [ {"material": "nombre_material", "cantidad": int}, {...} ]
    items : list


# Metodo GET para obtener todos los pedidos existentes en la db
# GET - /pedidos/todos
@router.get("/todos", response_model=None)
def get_pedidos_todos(db: Session = Depends(get_db)):
    
    ## TODO Verificar que el usuario tenga el token necesario

    logger.info("Devolviendo todos los pedidos")
    try:
        # Obteniendo todos los pedidos
        pedidos = Pedido.devolver_pedidos_todos(db)
        if (pedidos == None):
            raise HTTPException(status_code=404, detail="No se encontraron pedidos en la base de datos.")
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

# Metodo POST para insertar un nuevo pedido
# POST - /pedidos/insertar
@router.post("/insertar", response_model=None)
def insertar_pedido(pedido: PedidoDB, request: Request, db: Session = Depends(get_db)):
    
    ## TODO Verificar que el usuario tenga el token necesario
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Insertando nuevo pedido en la db
        logger.info(f"Insertando pedido para {pedido.cliente}")
        pedido = Pedido.insertar_pedido(pedido, db)
        return pedido
    except Exception as e:
        logger.error(f"Error insertando nuevo pedido. {e}")
        raise HTTPException(status_code=500, detail=f"Error insertando nuevo pedido. {e}")