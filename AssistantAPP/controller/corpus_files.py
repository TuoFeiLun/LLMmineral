"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 14:02  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from fastapi import Request
from pathlib import Path
import shutil
import os
from constantparas import vector_db_path
from database.corpusdb import insert_corpus, mark_converted, get_corpus, delete_corpus, get_all_corpus
from database.vectordb import insert_vectordb, get_by_collection_name
from rag.createDB import add_documents_to_collection, setup_models


files_router = APIRouter()


@files_router.post("/corpus_files")
async def upload_corpus_files(file: UploadFile = File(...)):
    """Upload a single corpus file, save to store_user_corpus, and add a DB record."""
    
    # Define supported file formats
    SUPPORTED_FORMATS = {
        '.pdf', '.docx', '.txt', '.json', '.csv', '.xlsx', 
        '.tiff', '.tif', '.jpg', '.jpeg', '.png'
    }
    
    try:
        # Validate file format
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_extension}. "
                       f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )
        
        # Validate file size (limit to 50MB)
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size allowed: 50MB"
            )
        
        # Reset file pointer for saving
        await file.seek(0)
        
        dest_dir = Path(__file__).parent.parent / "store_user_corpus"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename if file already exists
        dest_path = dest_dir / file.filename
        counter = 1
        while dest_path.exists():
            name_part = Path(file.filename).stem
            ext_part = Path(file.filename).suffix
            dest_path = dest_dir / f"{name_part}_{counter}{ext_part}"
            counter += 1
        
        # Save file
        with dest_path.open("wb") as fout:
            shutil.copyfileobj(file.file, fout)
        
        corpus_id = insert_corpus(file_name=dest_path.name, file_path=str(dest_path))
        
        return {
            "corpus_id": corpus_id, 
            "file_name": dest_path.name,
            "file_size": len(file_content),
            "file_type": file_extension,
            "message": "File uploaded successfully"
        }
        
    except HTTPException:
        raise
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


@files_router.get("/corpus_files")
async def get_all_corpus_files(limit: int = 50, offset: int = 0):
    """Get all corpus files with pagination and file size information."""
    try:
        corpus_files = get_all_corpus(limit=limit, offset=offset)
        
        # Add file size information for each file
        for corpus_file in corpus_files:
            file_path = Path(corpus_file["file_path"])
            if file_path.exists():
                corpus_file["file_size"] = file_path.stat().st_size
                corpus_file["file_exists"] = True
            else:
                corpus_file["file_size"] = None
                corpus_file["file_exists"] = False
            
            # Add file type information
            corpus_file["file_type"] = file_path.suffix.lower() if file_path.suffix else None
        
        return {
            "corpus_files": corpus_files,
            "total_returned": len(corpus_files),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get corpus files: {e}")


@files_router.get("/corpus_files/{corpus_id}")
async def get_corpus_file(corpus_id: int):
    """Get a single corpus file by ID with detailed information."""
    try:
        corpus_info = get_corpus(corpus_id)
        if not corpus_info:
            raise HTTPException(status_code=404, detail="Corpus file not found")
        
        # Add file size and existence information
        file_path = Path(corpus_info["file_path"])
        if file_path.exists():
            corpus_info["file_size"] = file_path.stat().st_size
            corpus_info["file_exists"] = True
        else:
            corpus_info["file_size"] = None
            corpus_info["file_exists"] = False
        
        # Add file type information
        corpus_info["file_type"] = file_path.suffix.lower() if file_path.suffix else None
        
        return corpus_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get corpus file: {e}")


@files_router.delete("/corpus_files/{corpus_id}")
async def delete_corpus_file(corpus_id: int):
    """Delete a corpus file and related records from database and filesystem."""
    try:
        # Check if corpus_id exists and get file info
        corpus_info = get_corpus(corpus_id)
        if not corpus_info:
            raise HTTPException(status_code=404, detail="Corpus file not found")
        
        # Delete physical file from filesystem
        file_path = Path(corpus_info["file_path"])
        if file_path.exists():
            file_path.unlink()  # Delete the file
        
        # Delete corpus record from database
        deleted = delete_corpus(corpus_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete corpus record from database")
        
        return {
            "message": "Corpus file deleted successfully",
            "corpus_id": corpus_id,
            "file_name": corpus_info["file_name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete corpus file: {e}")
     