from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import Session
from database import Base
from sqlalchemy.orm import relationship

class Material(Base):
    __tablename__ = 'material'

    idmaterial = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    nombre = Column(String(45), nullable=False, unique=True)
    descripcion = Column(String(45), nullable=False)
    # Relacion con Centro
    centros = relationship("Centro",secondary="centro_material", back_populates="materiales")

    def devolver_material(id, db: Session):
        try:
            material = db.query(Material).filter(Material.idmaterial == id).first()
            return material.nombre
        except Exception as e:
            raise (f"Error al devolver el material: {e}")
        
    def devolver_materiales_todos(db: Session):
            materiales = db.query(Material).all()
            return materiales
        
    def devolver_material_por_nombre(nombre, db: Session):
        try:
            material = db.query(Material).filter(func.lower(Material.nombre) == nombre.lower()).first()
            return material
        except Exception as e:
            raise (f"Error al devolver el material: {e}")
        
    def insertar_material(nombre,descr, db: Session):
        try:
            material = Material(nombre=nombre, descripcion = descr)
            db.add(material)
            db.commit()
            db.refresh(material)
            return material
        except Exception as e:
            raise (f"Error al insertar el material: {e}")