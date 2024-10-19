from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import Session
from database import Base
from sqlalchemy.orm import relationship
from models.material import Material

class Centro(Base):
    __tablename__ = 'centro'

    idcentro = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    nombre = Column(String(45), nullable=False)
    direccion = Column(String(45), nullable=False)
    ## Relación uno-a-muchos con Material
    materiales = relationship("Material", back_populates="centro")

    def devolver_centro(id, db: Session):
        try:
            centro = db.query(Centro).filter(Centro.idcentro == id).first()
            return centro.nombre
        except Exception as e:
            raise Exception(f"Error al devolver el centro: {e}")
        
    def devolver_centros_todos(db: Session):
        centros = db.query(Centro).all()
        return centros
        
    def devolver_centro_por_nombre(nombre, db: Session):
        try:
            centro = db.query(Centro).filter(func.lower(Centro.nombre) == nombre.lower()).first()
            return centro
        except Exception as e:
            raise (f"Error al devolver el centro: {e}")

    def insertar_centro(nombre: str, direccion, db: Session):
        try:
            nombre = nombre.upper()
            centro = Centro(nombre=nombre, direccion=direccion)
            db.add(centro)
            db.commit()
            db.refresh(centro)
            return centro
        except Exception as e:
            raise Exception(f"Error al insertar el centro: {e}")
    
    def referenciar_materiales(centro, materiales, db: Session):
        try:
            centro = Centro.devolver_centro_por_nombre(centro, db)
            for mat in materiales:
                material = Material.devolver_material_por_nombre(mat, db)
                if (material == None):
                    raise Exception(f"El material {mat} no existe")
                if (material in centro.materiales):
                    raise Exception(f"El material {mat} ya esta referenciado en el centro {centro.nombre}")
                centro.materiales.append(material)
                db.commit()
                db.refresh(centro)
            return centro
        except Exception as e:
            raise Exception(f"Error al referenciar los materiales: {e}")

    def insertar_centro_con_materiales(nombre, direccion, materiales, db: Session):
        try:
            centro = Centro.insertar_centro(nombre, direccion, db)
            Centro.referenciar_materiales(nombre, materiales, db)
            return centro
        except Exception as e:
            raise Exception(f"Error al insertar el centro con materiales: {e}") 