"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 17:42  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""

from fastapi import APIRouter
conversation_router = APIRouter()

@conversation_router.post("/conversation")
async def create_conversation(conversation: Conversation):
    """create a new conversation"""
    return conversation


async def get_conversation(conversation_id: int):
    """get a conversation"""
    return conversation_id


async def update_conversation(conversation_id: int, conversation: Conversation):
    """update a conversation"""
    return conversation_id

async def delete_conversation(conversation_id: int):
    """delete a conversation"""
    return conversation_id

async def get_all_conversation():
    pass