# import uvloop
from routers import app
from routers.userMaster import router as userRouter,routerApproval,routerToken
from routers.userOffers import useroffersRouter
from routers.userWallet import userWalletRouter
from routers.feedBackMaster import feedBackRouter
from routers.menuOptionsAccess import menuOptionAccessRouter
from routers.forgotPassword import forgotPasswordRouter
from routers.verifyOTP import verifyOTPRouter
from routers.signupOTP import signupOTPRouter
from routers.login import loginRouter
from routers.vehicleMaster import vehicleMasterRouter
from routers.addressMaster import addressMasterRouter
# from routers.fireBaseNotification import router as fireBaseNotification_Router
# uvloop.install()

app.include_router(userRouter)
app.include_router(useroffersRouter)
app.include_router(userWalletRouter)
app.include_router(feedBackRouter)
app.include_router(menuOptionAccessRouter)
app.include_router(forgotPasswordRouter)
app.include_router(verifyOTPRouter)
app.include_router(signupOTPRouter)
app.include_router(routerApproval)
app.include_router(routerToken)
app.include_router(loginRouter)
app.include_router(vehicleMasterRouter)
app.include_router(addressMasterRouter)
# app.include_router(fireBaseNotification_Router)

@app.get("/")
def read_root():
    return {"data": "Api running successfully"}


