
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import SECRET_KEY
from controller.query import query_router
from controller.conversation import conversation_router
from controller.corpus_files import files_router
from controller.rag_config import rag_manage_router
import uvicorn

app = FastAPI(
    title="Mineral Exploration Assistant API",
    description="API for geological data query and corpus management",
    version="1.0.0"
)
app.secret_key = SECRET_KEY

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173", 
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router, prefix='/v1/query')
app.include_router(conversation_router, prefix='/v1/conversation')
app.include_router(files_router, prefix='/v1/kb')
app.include_router(rag_manage_router, prefix='/v1/rag')

@app.get("/")
async def root():
    return {"message": "Mineral Assistant API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "assis_app:app", 
        host="0.0.0.0", 
        port=3000, 
        reload=True,
        timeout_keep_alive=300,  # 5 minutes keep alive
        timeout_notify=300,      # 5 minutes timeout notification
        limit_max_requests=1000,
        limit_concurrency=100
    )

 
#   uvicorn assis_app:app --host 0.0.0.0 --port 3000 --reload