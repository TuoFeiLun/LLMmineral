
from fastapi import FastAPI
from config import SECRET_KEY
from controller.query import query_router
from controller.conversation import conversation_router
from controller.corpus_files import files_router

app = FastAPI()
app.secret_key = SECRET_KEY

app.include_router(query_router, prefix='/v1/query')
app.include_router(conversation_router, prefix='/v1')
app.include_router(files_router, prefix='/v1')

 
#   uvicorn assis_app:app --host 0.0.0.0 --port 3000