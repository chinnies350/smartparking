# import uvloop
from routers import app
from routers.messageTemplates import messageTemplatesRouter
from routers.sendNotification import router as sendNotification_router
from routers.fireBaseNotification import router as fireBaseNotification_router

# uvloop.install()

app.include_router(messageTemplatesRouter)
app.include_router(sendNotification_router)
app.include_router(fireBaseNotification_router)


@app.get("/")
def read_root():
    return {"data": "Api running successfully"}


