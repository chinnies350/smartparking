from routers import app
from routers.offerMaster import offerRouter
from routers.offerRules import offerRulesRouter
from routers.offerMapping import offerMappingRouter



app.include_router(offerRouter)
app.include_router(offerRulesRouter)
app.include_router(offerMappingRouter)

@app.get("/")
def read_root():
    return {"data": "Api running successfully"}


