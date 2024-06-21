from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.utils import write_md_to_pdf
import time
import os
from gpt_researcher import GPTResearcher
import re


class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str


app = FastAPI()


# Dynamic directory for outputs once first research is run
@app.on_event("startup")
def startup_event():
    if not os.path.isdir("outputs"):
        os.makedirs("outputs")
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")



@app.get("/report")
async def get_report(query: str, report_type: str) -> dict:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    
    # Saving report as pdf
    filename = f"task_{int(time.time())}_{query[:50].replace(" ", "_")}"
    filename = make_filename_safe(filename)
    pdf_path = await write_md_to_pdf(report, filename)
    
    return {"report": report, "pdf_path": pdf_path}

def make_filename_safe(string, max_length=255):
    # Заменяем недопустимые символы и переводы строки на подчеркивание
    safe_string = re.sub(r'[\\/*?:"<>|\n\r]', '_', string)
    # Заменяем пробелы на подчеркивания
    safe_string = safe_string.replace(' ', '_')
    # Обрезаем строку, если она слишком длинная
    safe_string = safe_string[:max_length]
    return safe_string