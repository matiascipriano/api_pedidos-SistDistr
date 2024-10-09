from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from fastapi import HTTPException
from database import Base
from models.item import Item
from models.centro import Centro
from models.material import Material

class Pedido(Base):
    __tablename__ = 'pedido'

    idPedido = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    estado = Column(String(20), nullable=False)
    cliente = Column(String(100), nullable=False)
    # Este campo sera null si el pedido no esta "en progreso"
    idCentro = Column(Integer, ForeignKey('centro.idCentro'), nullable=True)
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
                    "Pedido": pedido.idPedido,
                    "Estado": pedido.estado,
                    "Cliente": pedido.cliente
                }
                if (estado == "en progreso" and pedido.idCentro != None):
                    obj["Centro"] = Centro.devolver_centro(pedido.idCentro, db)
                response.append(obj)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {e}")
        
    def insertar_pedido(data, db: Session):
        try:
            pedido = Pedido(estado="generado", cliente=data.get("cliente"))
            for mat in data.get("items"):
                material = Material.devolver_material_por_nombre(mat.get('material'), db)
                item = Item(
                    idMaterial=int(material.idMaterial),
                    cantidad=int(mat.get('cantidad'))
                )
                pedido.items.append(item)
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al insertar recoleccion: {e}")
