from routers import app
from routers.parkingPassConfig import parkingPassConfigRouter
from routers.passTransaction import passTransactionRouter


app.include_router(parkingPassConfigRouter)
app.include_router(passTransactionRouter)

@app.get("/")
def read_root():
    return {"data": "Api running successfully"}


