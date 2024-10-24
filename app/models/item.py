from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from models.material import Material
from database import Base

class Item(Base):
    __tablename__ = 'item'

    iditem = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    idmaterial = Column(Integer, ForeignKey('material.idmaterial'))
    idpedido = Column(Integer, ForeignKey('pedido.idpedido'))
    cantidad = Column(Integer, nullable=False)
    
    # Relación con Material
    material = relationship("Material")
    # Relacion con Pedido
    pedido = relationship("Pedido", back_populates="items")

    ## TODO un insert del item
    def insertar_item(id_mat,cant ,db: Session):
        try:
            item = Item(idMaterial=id_mat, cantidad=cant)
            db.add(item)
            db.commit()
            return item
        except Exception as e:
            raise Exception(f"Error al devolver la recoleccion: {e}")