"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 14:10  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""

from fastapi import APIRouter
rag_manage_router = APIRouter()

@rag_manage_router.get("/collection")
async def get_all_collection():
    """get collection for using"""

   

@rag_manage_router.post("/collection_using")
async def set_collection_using(collection_name: str):
    """set collection for using 
       collection status is true when using
    """
    return collection_name

