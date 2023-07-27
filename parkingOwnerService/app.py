# from fastapi import FastAPI
from routers import app
from routers.parkingOwnerMaster import router as parkingOwnerMaster_router
from routers.shiftMaster import router as shiftMaster_router
from routers.blockMaster import router as blockmaster_router
from routers.admin import router as admin_router
from routers.branchMaster import router as branch_router
from routers.branchWorkingHrs import router as branchWorkingHrs_router
from routers.printingInstructionsConfig import router as printingInstructionsConfig_router
from routers.printingInstructionsConfig import router1 as printingInstructionsConfig_router1
from routers.cancellationRules import router as cancellationRules_router
from routers.employeeMaster import router as employeeMaster_router
from routers.getBranchDetails import dateTimeRouter
from routers.paymentUPIDetails import router as paymentUPIDetails_router
# app = FastAPI(
#     # root_path='booking',           
#     # openapi_prefix='/booking',
#     # # openapi_url="/booking/openapi.json",
#     # docs_url="/booking/docs",
#     )


app.include_router(parkingOwnerMaster_router)
app.include_router(shiftMaster_router)
app.include_router(blockmaster_router)
app.include_router(admin_router)
app.include_router(branch_router)
app.include_router(branchWorkingHrs_router)
app.include_router(printingInstructionsConfig_router)
app.include_router(printingInstructionsConfig_router1)
app.include_router(cancellationRules_router)
app.include_router(employeeMaster_router)
app.include_router(dateTimeRouter)
app.include_router(paymentUPIDetails_router)
# app.include_router(branchbasedondatetime_router)


@app.get("/")
def read_root():
    return {"data": "Api running successfully"}