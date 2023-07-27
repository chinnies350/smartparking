from routers import app
from routers.subscriptionMaster import subscriptionRouter
from routers.userSubscription import userSubscriptionRouter

app.include_router(subscriptionRouter)
app.include_router(userSubscriptionRouter)

@app.get("/")
def read_root():
    return {"data": "Api running successfully"}