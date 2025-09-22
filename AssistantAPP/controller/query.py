"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/22 12:41  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""
import sys
from pathlib import Path
# Add project root to Python path (go up 2 levels: controller -> AssistantAPP -> project root)
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
print(sys.path)

from fastapi import APIRouter, Query, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from rag.createDB import load_existing_database, test_queries2, setup_models
from datetime import timezone
from config import SECRET_KEY, vector_db_path
from model.queryquestion import QueryQuestion
import time
from datetime import datetime
from database.creatSQL import get_llm_model_id_by_name
from database.queryquestiondb import insert_queryquestion
query_router = APIRouter()
security = HTTPBearer()
index = None

setup_models()
try:
    index = load_existing_database(vector_db_path)
except Exception as e:
    raise HTTPException(status_code=500, detail="load database failed")

@query_router.post("/send_query")
async def send_query(query: QueryQuestion):
    """user will send a query to the assistant,
    the assistant will return the answer to the user
    """
    try:
        if index is None:
            raise HTTPException(status_code=500, detail="database not loaded")
        
        queries = [query.query]
        send_ts = datetime.utcnow().isoformat()
        start_time = time.time()
        result = test_queries2(index, queries)
        print(f"conversation_id: {query.conversation_id}")
        end_time = time.time()
        finish_ts = datetime.utcnow().isoformat()
        elapsed = end_time - start_time
        print(f"time taken: {elapsed} seconds")

        # resolve model id
        llm_id = None
        if query.llmmodel_id:
            llm_id = query.llmmodel_id
        else:
            llm_id = get_llm_model_id_by_name(query.model_name or "qwen2.5-7b")

        sources_text = "\n".join(result.get("sources", []) or [])
        insert_queryquestion(
            question=query.query,
            llmmodel_id=llm_id or 1,
            conversation_id=query.conversation_id,
            answer=result.get("answer", ""),
            sourcetrace=sources_text,
            thinktime=elapsed,
            send_time=send_ts,
            finish_time=finish_ts,
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="query failed")

    
    return JSONResponse(status_code=200, content=result)

 