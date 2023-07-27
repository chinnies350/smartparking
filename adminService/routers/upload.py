from sqlite3 import Cursor
from fastapi.routing import APIRouter
from fastapi import Depends
from routers.config import get_cursor,db,Base_Url
from dotenv import load_dotenv
from fastapi import File, UploadFile
import gridfs
from bson import ObjectId
from starlette.responses import StreamingResponse
import io

load_dotenv()

uploadRouter = APIRouter(prefix='/Upload')


@uploadRouter.get('')
async def getUpload(fileId: str):
    try:
        fileId = fileId.split("=")[-1]
        fileId, fileEtension = fileId.split(".")
        image = fileId
        fs = gridfs.GridFS(db)
        img = fs.get(ObjectId(image))
        return StreamingResponse(io.BytesIO(img.read()), media_type=f"image/{fileEtension}")
    except Exception as e:
        print("Exception as getUpload ",str(e))
        return {"statusCode": 0, "response":"Server Error"}

@uploadRouter.post('')
async def create_upload_file(image: UploadFile = File(...)):
    try:
        fileExtension = image.filename.split(".")[-1]
        contents = await image.read()
        fs = gridfs.GridFS(db)
        img = fs.put(contents)
        img_url = Base_Url+"Upload?fileId="+str(img) + '.'+str(fileExtension)
        return {'response': img_url, 'statusCode': 1}
    except Exception as e:
        print("Exception as create_upload_file ",str(e))
        return {'response':"Server Error", 'statusCode': 0}


