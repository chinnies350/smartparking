from fastapi import FastAPI
import httpx
import json

app = FastAPI(title="admin service")

@app.on_event("startup")
async def startup():
    global client
    client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()


def Response(data):
    with open('routers/constants/http_status_codes.json') as f:
        dic = json.load(f)
        return dic[data]
