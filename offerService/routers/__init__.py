from fastapi import FastAPI
import httpx
import http.client

app = FastAPI()

client = ""

@app.on_event("startup")
async def startup():
    global client
    client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown():
    await client.close()