"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 17:42  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.conversationdb import (
    create_conversation as db_create_conversation,
    get_conversation as db_get_conversation,
    list_conversations as db_list_conversations,
    delete_conversation as db_delete_conversation,
)
from database.queryquestiondb import get_queries_by_conversation


class ConversationCreate(BaseModel):
    pass


conversation_router = APIRouter()


@conversation_router.post("/conversation")
async def create_conversation():
    """Create a new conversation and return its id."""
    conv_id = db_create_conversation()
    return {"id": conv_id}


@conversation_router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: int):
    """Get a conversation by id."""
    rec = db_get_conversation(conversation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return rec


@conversation_router.get("/conversations")
async def get_all_conversation(limit: int = 50, offset: int = 0):
    """Get all conversations with pagination."""
    conversations = db_list_conversations(limit=limit, offset=offset)
    return {
        "conversations": conversations,
        "count": len(conversations),
        "limit": limit,
        "offset": offset
    }


@conversation_router.get("/conversation/{conversation_id}/queries")
async def get_conversation_queries(conversation_id: int):
    """Get all queries and responses for a specific conversation."""
    # First check if conversation exists
    conversation = db_get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get all queries for this conversation
    queries = get_queries_by_conversation(conversation_id)
    return {"conversation_id": conversation_id, "queries": queries}


@conversation_router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: int):
    if not db_delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}