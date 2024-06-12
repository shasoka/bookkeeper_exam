from fastapi import FastAPI

from database.router import router as databse_router
from sections.router import router as sections_router
from themes.router import router as themes_router
from questions.router import router as questions_router


app = FastAPI()
app.include_router(databse_router)
app.include_router(sections_router)
app.include_router(themes_router)
app.include_router(questions_router)
