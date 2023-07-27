# from fastapi import FastAPI
from routers.booking import router as booking_router
from routers.distanceCalculation import router as distanceCalculation_router
from routers.vehicleheader import router as vehicleHeader_router
from routers.extraFeatures import router as extraFeatures_router
from routers.extrafees import router as extraFees_router
from routers.userslot import router as userSlot_router
from routers.booking import routerDateTimeExtend as DateTimeExtend_router
from routers.booking import routerpaidAmount as paidAmount_router
from routers.passbooking import router as passbooking_router
from routers.generatePin import generatePinRouter
from routers.cancellationDetails import cancellationDetailsRouter
from routers.passBookingTransaction import passBookingTransactionRouter
from routers.getDataBasedOnSlotId import router as getDataBasedOnSlotId
from routers.paymentTransactionHistory import paymentTransactionHistoryRouter
from routers.getDataBasedOnVehicleNumberAndPhone import router as getDataBasedOnVehicleNumberAndPhone
from routers import app
# import uvloop

# uvloop.install()

# app = FastAPI(
#     # root_path='booking',           
#     # openapi_prefix='/booking',
#     # # openapi_url="/booking/openapi.json",
#     # docs_url="/booking/docs",
#     )


app.include_router(booking_router)
app.include_router(distanceCalculation_router)
app.include_router(vehicleHeader_router)
app.include_router(extraFeatures_router)
app.include_router(extraFees_router)
app.include_router(userSlot_router)
app.include_router(DateTimeExtend_router)
app.include_router(paidAmount_router)
app.include_router(passbooking_router)
app.include_router(generatePinRouter)
app.include_router(cancellationDetailsRouter)
app.include_router(passBookingTransactionRouter)
app.include_router(getDataBasedOnSlotId)
app.include_router(paymentTransactionHistoryRouter)
app.include_router(getDataBasedOnVehicleNumberAndPhone)



@app.get("/")
def read_root():
    return {"data": "Api running successfully"}