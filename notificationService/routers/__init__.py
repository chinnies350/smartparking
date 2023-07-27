from fastapi import FastAPI
import httpx

app = FastAPI(title="notification service")


@app.on_event("startup")
async def startup():
    global client
    client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()



