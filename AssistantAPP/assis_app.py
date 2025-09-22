
from fastapi import FastAPI
from config import SECRET_KEY
from controller.query import query_router

app = FastAPI()
app.secret_key = SECRET_KEY

app.include_router(query_router, prefix='/v1/query')

 
#   uvicorn assis_app:app --host 0.0.0.0 --port 3000