from pydantic import BaseModel
from typing import Optional,Dict,List

class CVInput(BaseModel):
    cv_text:str

class Education(BaseModel):
    degree_title:str
    university:str
    cgpa:float
    date:str
class LLMOutput(BaseModel):
    name:str
    education:Education
    skills:List[str]
    experience_years:int
    suggested_roles:List[str]