"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 14:02  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""
from fastapi import APIRouter, UploadFile, File
from typing import List
from fastapi import Request
import asyncio
files_router = APIRouter()

@files_router.post("/corpus_files")
async def upload_corpus_files(files: UploadFile = File(...)):
    """upload files 
       setting collection name for the vector database
    """
    
    return {"message": "Files uploaded successfully"}   


@files_router.post("/corpus_files_to_vector_database")
async def convert_files_to_vector_database(request: Request):
    """convert files to vector database 
        set collecction name（unique） 
    """
    data = await request.json()

    