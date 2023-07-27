from linecache import cache
from fastapi.routing import APIRouter
# from routers.config import cacheClient
import time

router = APIRouter(prefix='/distanceCalculation')


@router.get("/")
def getDistance(latitude: float, longitude: float):
    start = time.time()
    var = cacheClient.georadius('geospatial_stored_set', str(latitude), str(longitude), 100, unit='km', withdist=True, withcoord=True)
    print(f'time {time.time() - start} val {var}')
    return {"response": "Api running successfully"}

