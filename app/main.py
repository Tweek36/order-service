from fastapi import FastAPI

app = FastAPI(
    title="Order Service",
    description="API для управления заказами",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "healthy"}
