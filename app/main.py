from fastapi import FastAPI

app = FastAPI(
    title="PeludOS API",
    description="API para la plataforma de cuidado de mascotas",
    version="0.1.0",
)


@app.get("/health", tags=["Salud"])
def health_check():
    """
    Endpoint simple para verificar que la API está corriendo
    y respondiendo correctamente.
    """
    return {"status": "ok", "app": "PeludOS API"}