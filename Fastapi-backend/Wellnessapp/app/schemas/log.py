from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LogCreate(BaseModel):
    req_url: str
    method: str
    req_param: Optional[str] = None
    res_param: Optional[str] = None
    msg: str
    code: int
    time_stamp: datetime

class Log(LogCreate):
    id: int
