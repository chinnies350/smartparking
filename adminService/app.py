from routers import app
# import uvloop

from routers.configMaster import configMasterRouter
from routers.vehicleConfigMaster import vehicleConfigRouter
from routers.taxMaster import taxRouter
from routers.menuOptions import menuOptionsRouter
from routers.configType import configTypeRouter
from routers.faq import faqRouter
from routers.appSettings import appSettingsRouter
from routers.chargePinConfig import chargePinConfigRouter
from routers.upload import uploadRouter
from routers.parkingOwnerConfig import parkingOwnerConfigRouter
from routers.sample import sampleRouter
# uvloop.install()

app.include_router(configMasterRouter)
app.include_router(vehicleConfigRouter)
app.include_router(taxRouter)
app.include_router(menuOptionsRouter)
app.include_router(configTypeRouter)
app.include_router(faqRouter)
app.include_router(appSettingsRouter)
app.include_router(chargePinConfigRouter)
app.include_router(uploadRouter)
app.include_router(parkingOwnerConfigRouter)
app.include_router(sampleRouter)