# Ecocycle -- Grupo11 -- Sistemas Distribuidos
Grupo 11 - Desarrollo de Software en Sistemas Distribuidos

## Estructura del proyecto
En la carpeta /app se encuentran las carpetas:
- routes/ con los endpoints de la API
- models/ con la logica de base de datos
- helpers/ funciones extras de ayuda
En la carpeta /frontend se encuentran los archivos:
- src/
    - App.jsx -- Con el router de todo el front
    - components/ con los archivos front que pueden crearse

## Backend
Mediante FastAPI se pueden implementar endpoints que sirvan para la logica de negocio y manejo de base de datos.

## PostgreSQL
Se usara una base de datos postgres.

### Tablas
- Pedido
    - Compuesto por estado, cliente y una lista de items.
        - En caso de que este en estado "en progreso" tiene un idCentro.
    - Estados:
        - "generado"
        - "en progreso"
        - "finalizado"
- Item
    - Compuesto por idMaterial y cantidad.
- Material
- Usuario