from fastapi import APIRouter
from task import postVehicleName

sampleRouter = APIRouter(prefix='/sample', tags=['sample'])


@sampleRouter.get('')
def home():
    postVehicleName.delay(10,'mohan','madurai')
    return 'hello dhanalakshmi'