# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models import Base # Importar Base para la creación de tablas
from data.models import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, # Importa JugadorResponse
    MascotaCreate, MascotaUpdate, MascotaResponse, # Importa EquipoResponse
    VueloCreate, VueloUpdate, VueloResponse, # Importa PartidoResponse
    Usuario, Mascota, Vuelo # Importa los modelos ORM Jugador, Equipo, Partido si se usan directamente en el código
)
from operations import usuarios_operations, mascotas_operations, vuelos_operations # Importar operaciones de partidos
from routes import html_pages # Asegúrate de que html_pages esté importado
import uvicorn
from datetime import date # Necesario para los campos de fecha en la API de partidos

# Cargar variables de entorno del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env o en el entorno.")

# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear todas las tablas si no existen.
# Esto es útil para el desarrollo local.
# En Render, esto se manejará con el comando de build 'python populate_db.py'.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Champions League 2017/18 Data API",
    description="Una API para gestionar datos de equipos, jugadores y partidos de la UEFA Champions League 2017/18.",
    version="1.0.0",
)

# Montar el directorio estático para servir css, JS, imágenes, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir los routers de las páginas HTML
app.include_router(html_pages.router)

# Redirección de la raíz a la página de inicio
@app.get("/", response_class=HTMLResponse, tags=["Inicio"])
async def root(request: Request):
    # Redirigimos a la ruta de la página de inicio en html_pages.py
    return RedirectResponse(url="/home", status_code=302)


# ---------------- USUARIOS (Endpoints API JSON) ----------------
# Estos endpoints son para la API RESTful (JSON).

@app.post("/api/Usuario", response_model=UsuarioResponse, tags=["API Usuario"])
async def crear_Usuario_api(
    Usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    try:
        return usuarios_operations.create_jugador(db, Usuario)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear jugador: {e}")


@app.get("/api/Usuario", response_model=list[UsuarioResponse], tags=["API Usuario"])
def obtener_Usuario_api(db: Session = Depends(get_db)):
    Usuario = usuarios_operations.get_all_Usuario(db)
    if not Usuario:
        raise HTTPException(status_code=404, detail="No hay Usuarios registrados")
    return Usuario

@app.get("/api/Usuarios/buscar", response_model=list[UsuarioResponse], tags=["API Usuario"])
def buscar_Usuario_api(
    nombre: str = Query(None),
    edad: int = Query(None),
    nacionalidad: str = Query(None),
    eliminado: bool = Query(False), # Por defecto, busca no eliminados
    db: Session = Depends(get_db)
):
    resultados = usuarios_operations.search_jugadores(
        db=db,
        nombre=nombre,
        edad=edad,
        nacionalidad=nacionalidad,
        eliminado=eliminado
    )
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron Usuarios que coincidan con los filtros")
    return resultados


@app.get("/api/Usuario/{Usuario_id}", response_model=UsuarioResponse, tags=["API Usuario"])
def obtener_Usuario_api(Usuario_id: int, db: Session = Depends(get_db)):
    Usuario = usuarios_operations.get_Usuario_by_id(db, Usuario_id)
    if not Usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Usuario

@app.put("/api/Usuario/{Usuario_id}", response_model=UsuarioResponse, tags=["API Usuario"])
async def actualizar_Usuario_api(
    Usuario_id: int,
    Usuario: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    actualizado = usuarios_operations.update_Usuario(db, Usuario_id, Usuario)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    return actualizado

@app.delete("/api/Usuario/{Usuario_id}", tags=["API Usuario"])
def eliminar_Usuario_api(Usuario_id: int, db: Session = Depends(get_db)):
    eliminado = usuarios_operations.soft_delete_Usuario(db, Usuario_id) # Usamos soft_delete
    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario  eliminado lógicamente"}

# ---------------- MASCOTAS (Endpoints API JSON) ----------------

@app.post("/api/Mascota", response_model=MascotaResponse, tags=["API Mascota"])
def crear_Mascota_api(Mascota: MascotaCreate, db: Session = Depends(get_db)):
    try:
        return mascotas_operations.create_mascota(db, Mascota)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear Mascota: {e}")

@app.get("/api/Mascota", response_model=list[MascotaResponse], tags=["API Mascota"])
def obtener_Mascota_api(db: Session = Depends(get_db)):
    Mascota = mascotas_operations.get_all_mascotas(db)
    if not Mascota\:
        raise HTTPException(status_code=404, detail="No hay Mascota registrados")
    return Mascota

@app.get("/api/Mascota/buscar", response_model=list[MascotaResponse], tags=["API Mascota"])
def buscar_Mascota_api(
    nombre: str = Query(None),
    tipo: str = Query(None),
    raza: str = Query(None),
    imagen_url = Query(None),
    eliminado: bool = Query(False), # Por defecto, busca no eliminados
    db: Session = Depends(get_db)
):
    resultados = mascotas_operations.search_mascotas(
        db=db,
        nombre=nombre,
        tipo=tipo,
        raza=raza,
        imagen_url=imagen_url,
        eliminado=eliminado
    )
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron equipos que coincidan con los filtros")
    return resultados

@app.get("/api/Mascotas/{Mascota_id}", response_model=MascotaResponse, tags=["API Mascota"])
def obtener_equipo_api(Mascota_id: int, db: Session = Depends(get_db)):
    Mascota = mascotas_operations.get_mascota_by_id(db, Mascota_id)
    if not Mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrado")
    return Mascota

@app.put("/api/Mascotas/{Mascota_id}", response_model=MascotaResponse, tags=["API Mascota"])
def actualizar_Mascota_api(Mascota_id: int, Mascota: MascotaUpdate, db: Session = Depends(get_db)):
    actualizado = mascotas_operations.update_mascota(db, Mascota_id, Mascota)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return actualizado

@app.delete("/api/Mascotas/{Mascota_id}", tags=["API Mascota"])
def eliminar_Mascota_api(Mascota_id: int, db: Session = Depends(get_db)):
    eliminado = mascotas_operations.soft_delete_mascota(db, Mascota_id) # Usamos soft_delete
    if not eliminado:
        raise HTTPException(status_code=404, detail="Mascota no encontrado")
    return {"mensaje": "Mascota eliminado lógicamente"}

# ---------------- VUELOS(Endpoints API JSON) ----------------

@app.post("/api/Vuelo", response_model=VueloResponse, tags=["API Vuelos"])
async def crear_Vuelo_api(
    Vuelo: VueloCreate,
    db: Session = Depends(get_db)
):
    try:
        # Validar que los equipos existan y no estén eliminados lógicamente
        Vuelo_origen = vuelos_operations.get_Usuario_by_id(db, Usuario.Vuelo_origen_id)
        Vuelo_destino = vuelos_operations.get_Usuario_by_id(db, Vuelo.Usuario_destino_id)

        if not Vuelo_origen or Vuelo_origen.eliminado_logico:
            raise HTTPException(status_code=400, detail="Vuelo local no válido o eliminado lógicamente.")
        if not Vuelo_destino or Vuelo_destino.eliminado_logico:
            raise HTTPException(status_code=400, detail="Vuelo destino no válido o eliminado lógicamente.")
        if Vuelo.Usuario_origen_id == Vuelo.Usuario_destino_id:
            raise HTTPException(status_code=400, detail="El Vuelo origen y el destino no pueden ser el mismo.")

        return vuelos_operations.create_Vuelo(db, Vuelo)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear Vuelo: {e}")

@app.get("/api/Vuelo", response_model=list[VueloResponse], tags=["API Vuelos"])
def obtener_Vuelo_api(db: Session = Depends(get_db)):
    Vuelo = vuelos_operations.get_all_Vuelo(db)
    if not Vuelo:
        raise HTTPException(status_code=404, detail="No hay Vuelos registrados")
    return Vuelo

@app.get("/api/Vuelo/buscar", response_model=list[VueloResponse], tags=["API Vuelos"])
def buscar_Vuelo_api(
    Vuelo_nombre: str = Query(None),
    id_usuario: int = Query(None),
    origen: str = Query(None),
    destino: str = Query(None),
    fecha: int = Query(None),
    eliminado: bool = Query(False),
    db: Session = Depends(get_db)
):
    resultados = vuelos_operations.search_partidos(
        db=db,
        Vuelo_nombre=Vuelo_nombre,
        id_usuario=id_usuario,
        origen=origen,
        destino=destino,
        fecha=fecha,
        eliminado=eliminado
    )
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron Vuelos que coincidan con los filtros.")
    return resultados

@app.get("/api/Vuelo/{Vuelo_id}", response_model=VueloResponse, tags=["API Vuelo"])
def obtener_Vuelo_api(Vuelo_id: int, db: Session = Depends(get_db)):
    Vuelo = vuelos_operations.get_vuelo_by_id(db, Vuelo_id)
    if not Vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return Vuelo

@app.put("/api/Vuelo/{Vuelo_id}", response_model=VueloResponse, tags=["API Vuelo"])
async def actualizar_Vuelo_api(
    Vuelo_id: int,
    Vuelo: VueloUpdate,
    db: Session = Depends(get_db)
):
    try:
        # Validar que los equipos existan y no estén eliminados lógicamente
        if Vuelo.Mascota_origen_id:
            Vuelo_origen = usuarios_operations.get_Usuario_by_id(db, Vuelo.Usuario_origen_id)
            if not Vuelo_origen or Vuelos_destino.eliminado_logico:
                raise HTTPException(status_code=400, detail="Vuelo origen no válido o eliminado lógicamente.")
        if Vuelo.Usuario_destino_id:
            Usuario_destino = usuarios_operations.get_Usuario_by_id(db, Usuario.equipo_visitante_id)
            if not Usuario_destino or Usuario_destino.eliminado_logico:
                raise HTTPException(status_code=400, detail="Vuelo destino no válido o eliminado lógicamente.")
        if Vuelo.Usuario_origen_id and Usuario.Usuario_destino_id and Usuario.Usuario_origen_id == Usuario.Usuario_destino_id:
            raise HTTPException(status_code=400, detail="El Vuelo origen y el destino no pueden ser el mismo.")

        actualizado = vuelos_operations.update_Vuelo(db, Vuelo_id, Vuelo)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Vuelo no encontrado")
        return actualizado
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al Vuelo partido: {e}")

@app.delete("/api/Vuelo/{Vuelo_id}", tags=["API Vuelo"])
def eliminar_Vuelo_api(Vuelo_id: int, db: Session = Depends(get_db)):
    eliminado = vuelos_operations.soft_delete_partido(db, Vuelo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return {"mensaje": "Vuelo eliminado lógicamente"}


# Si ejecutas directamente este archivo
if __name__ == "__main__":
    # Para ejecutar con uvicorn directamente desde el script
    # Esto es útil para el desarrollo local
    uvicorn.run(app, host="0.0.0.0", port=8001)
