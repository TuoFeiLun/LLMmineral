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
    return db_list_conversations(limit=limit, offset=offset)


@conversation_router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: int):
    if not db_delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}