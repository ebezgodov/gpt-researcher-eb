from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.utils import write_md_to_pdf
import time
import os
import logging
from contextlib import asynccontextmanager
from gpt_researcher import GPTResearcher


class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    try:
        if not os.path.isdir("outputs"):
            os.makedirs("outputs")
        logging.info(f"Successfully created the outputs directory.")
    except Exception as e:
        logging.error(f"An error occurred while creating the outputs directory: {str(e)}")
        raise e
    finally:
        # Cleanup if needed in the future
        yield

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/report")
async def get_report(query: str, report_type: str) -> dict:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    
    # Saving report as pdf
    filename = f"task_{int(time.time())}_{query[:50].replace(" ", "_")}"
    pdf_path = await write_md_to_pdf(report, filename)
    
    return {"report": report, "pdf_path": pdf_path}
