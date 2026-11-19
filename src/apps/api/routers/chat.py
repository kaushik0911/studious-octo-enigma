from fastapi import APIRouter
from pydantic import BaseModel

from agent import agent
from helpers import do_profiling


class ChatQuery(BaseModel):
    user_id: str
    message: str


router = APIRouter()


@router.post("/chat", tags=["chat"])
@do_profiling
async def chat_endpoint(payload: ChatQuery):

    inputs = {"messages": [("user", payload.message)]}

    # Execute agent
    response = agent.invoke(inputs)
    final_message = response["messages"][-1].content

    return {"reply": final_message}
