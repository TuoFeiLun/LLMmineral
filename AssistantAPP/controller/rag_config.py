"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 14:10  
@ModifiedBy  : Yujia LI
@Description : RAG configuration management for vector database collections
@Version     : 0.0.1
@License     : None
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database.vectordb import (
    get_by_collection_name, 
    set_using_status, 
    get_all_vectordatabases, 
    get_active_collections,
    delete_vectordb_by_name
)

rag_manage_router = APIRouter()


class CollectionStatusUpdate(BaseModel):
    collection_name: str
    using_status: bool


def _get_collection_or_404(collection_name: str) -> Dict[str, Any]:
    """Helper function to get collection or raise 404 if not found."""
    collection = get_by_collection_name(collection_name)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    return collection



@rag_manage_router.get("/collection")
async def get_all_collection():
    """Get all vector database collections."""
    try:
        collections = get_all_vectordatabases()
        return {
            "total": len(collections),
            "collections": collections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collections: {e}")


@rag_manage_router.get("/collection/active")
async def get_active_collection():
    """Get only active collections (using_status=true)."""
    try:
        collections = get_active_collections()
        return {
            "total": len(collections),
            "active_collections": collections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active collections: {e}")


@rag_manage_router.get("/collection/{collection_name}")
async def get_collection_info(collection_name: str):
    """Get information about a specific collection."""
    try:
        collection = _get_collection_or_404(collection_name)
        # Convert using_status to boolean
        collection["using_status"] = bool(collection["using_status"])
        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {e}")


@rag_manage_router.post("/collection/status")
async def set_collection_using(status_update: CollectionStatusUpdate):
    """Set collection using status (enable/disable collection for use)."""
    print(status_update.collection_name)
    print(status_update.using_status)
    try:
        collection = _get_collection_or_404(status_update.collection_name)
        print(collection)
        # Update using status
        new_status = 1 if status_update.using_status else 0
        set_using_status(collection["id"], new_status)
        
        return {
            "collection_name": status_update.collection_name,
            "using_status": status_update.using_status,
            "message": f"Collection '{status_update.collection_name}' status updated to {'active' if status_update.using_status else 'inactive'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update collection status: {e}")


@rag_manage_router.post("/collection/{collection_name}/enable")
async def enable_collection(collection_name: str):
    """Enable a collection for use (set using_status=true)."""
    try:
        collection = _get_collection_or_404(collection_name)
        set_using_status(collection["id"], 1)
        return {
            "collection_name": collection_name,
            "using_status": True,
            "message": f"Collection '{collection_name}' enabled"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable collection: {e}")


@rag_manage_router.post("/collection/{collection_name}/disable")
async def disable_collection(collection_name: str):
    """Disable a collection (set using_status=false)."""
    try:
        collection = _get_collection_or_404(collection_name)
        set_using_status(collection["id"], 0)
        return {
            "collection_name": collection_name,
            "using_status": False,
            "message": f"Collection '{collection_name}' disabled"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable collection: {e}")


@rag_manage_router.delete("/collection/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection from the database (WARNING: This will also remove associated corpus records)."""
    try:
        # Check if collection exists first
        _get_collection_or_404(collection_name)
        
        # Delete the collection (this will set corpus.vectordatabase_id to NULL due to ON DELETE SET NULL)
        deleted = delete_vectordb_by_name(collection_name)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        return {
            "collection_name": collection_name,
            "message": f"Collection '{collection_name}' deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete collection: {e}")

