from pydantic import BaseModel

class AnswerSubmission(BaseModel):
    answer: str