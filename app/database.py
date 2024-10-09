from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
import os

# Acceder a las variables de entorno
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

# Utilizar las variables de entorno para la configuración
DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Declarar una clase base para las clases de modelo
Base = declarative_base()

# Crear una sesión de base de datos
SessionLocal = sessionmaker()
SessionLocal.configure(bind=engine)