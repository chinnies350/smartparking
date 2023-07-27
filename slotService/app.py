from routers import app
from routers.floorMaster import floorRouter
from routers.floorVehicleMaster import router as floorVehicleMaster_router
from routers.parkingLotLine import router as parkingLotLine_router
from routers.floorfeatures import router as floorfeatures_router
from routers.pricemaster import router as pricemaster_router
from routers.timeSlabRules import timeSlabRulesRouter
from routers.parkingSlot import parkingSlotRouter

# import uvloop

# uvloop.install()

app.include_router(floorRouter)
app.include_router(floorVehicleMaster_router)
app.include_router(parkingLotLine_router)
app.include_router(floorfeatures_router)
app.include_router(pricemaster_router)
app.include_router(timeSlabRulesRouter)
app.include_router(parkingSlotRouter)


@app.get("/")
def read_root():
    return {"data": "slot management running successfully"}


