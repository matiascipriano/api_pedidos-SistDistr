from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from fastapi import HTTPException
from database import Base
from models.item import Item
from models.centro import Centro
from models.material import Material
from helpers.logging import logger


class Pedido(Base):
    __tablename__ = 'pedido'

    idpedido = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    estado = Column(String(20), nullable=False)
    cliente = Column(String(100), nullable=False)
    # Este campo sera null si el pedido no esta "en progreso"
    idcentro = Column(Integer, ForeignKey('centro.idcentro'), nullable=True)
    # Relaciones
    centro = relationship("Centro")
    ## Relación uno-a-muchos con Item
    items = relationship("Item", back_populates="pedido", cascade="all, delete-orphan")

    def devolver_pedidos_todos(db: Session):
        try:
            pedidos = db.query(Pedido).all()
            return pedidos
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al devolver los pedidos: {e}")

    def devolver_pedidos_por_estado(estado, db: Session):
        try:
            response = []
            pedidos = db.query(Pedido).filter(Pedido.estado == estado).any()
            for pedido in pedidos:
                obj = {
                    "Pedido": pedido.idpedido,
                    "Estado": pedido.estado,
                    "Cliente": pedido.cliente
                }
                if (estado == "en progreso" and pedido.idcentro != None):
                    obj["Centro"] = Centro.devolver_centro(pedido.idcentro, db)
                response.append(obj)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {e}")
        
    def insertar_pedido(data, db: Session):
        try:
            items =[]
            for mat in data.items:
                material = Material.devolver_material_por_nombre(mat["material"], db)
                item = Item(
                    idmaterial=int(material.idmaterial),
                    cantidad=int(mat["cantidad"])
                )
                items.append(item)
            pedido = Pedido(estado="generado", cliente=data.cliente,items=items)
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            logger.error(f"Error en modelo pedido. {e}")
            raise HTTPException(status_code=500, detail=f"Error al insertar recoleccion: {e}")
