from pydantic import BaseModel

class LogIn(BaseModel):
    doctorName: str
    reason: str
    patientId: str
    logTime: int
    message: str


class LogOut(BaseModel):
    sender: str
    blockTimestamp: int
    doctorName: str
    reason: str
    patientId: str
    logTime: int
    message: str
