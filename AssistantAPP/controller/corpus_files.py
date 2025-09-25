"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 14:02  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from fastapi import Request
from pathlib import Path
import shutil
from constantparas import vector_db_path
from database.corpusdb import insert_corpus, mark_converted
from database.vectordb import insert_vectordb, get_by_collection_name
from rag.createDB import add_documents_to_collection, setup_models


files_router = APIRouter()


@files_router.post("/corpus_files")
async def upload_corpus_files(file: UploadFile = File(...)):
    """Upload a single corpus file, save to store_user_corpus, and add a DB record."""
    try:
        dest_dir = Path(__file__).parent.parent / "store_user_corpus"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / file.filename
        with dest_path.open("wb") as fout:
            shutil.copyfileobj(file.file, fout)
        corpus_id = insert_corpus(file_name=file.filename, file_path=str(dest_path))
        return {"corpus_id": corpus_id, "file_name": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@files_router.post("/corpus_files_to_vector_database")
async def convert_files_to_vector_database(request: Request):
    """Convert uploaded corpus directory to vector DB with a unique collection name."""
    data = await request.json()
    collection_name = data.get("collection_name")
    if not collection_name:
        raise HTTPException(status_code=400, detail="collection_name is required")

    # Ensure unique collection
    existing = get_by_collection_name(collection_name)
    if existing:
        raise HTTPException(status_code=400, detail="collection_name already exists")

    # Build data path: convert all files under store_user_corpus
    data_path = str((Path(__file__).parent.parent / "store_user_corpus").resolve())
    db_path = vector_db_path

    try:
        setup_models()
        index = add_documents_to_collection(data_path=data_path, db_path=db_path, collection_name=collection_name, update_mode="append")
        if not index:
            raise ValueError("index creation failed")
        vdb_id = insert_vectordb(collection_name=collection_name, db_path=db_path)
        # Note: To link specific corpus files to this vectordb, you would need to
        # track corpus_ids and call mark_converted(corpus_id, vdb_id) for each
        return {"collection_name": collection_name, "vectordb_id": vdb_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"convert failed: {e}")