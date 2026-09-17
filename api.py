from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Annotated
import os
import os.path
from database import get_completed_db, week_view_db, add_habit_db, initiate_db, delete_habit_db, complete_habit_db
import sqlite3



@asynccontextmanager
async def lifespan(app:FastAPI):
    if not os.path.exists("data"):
        os.mkdir("data")
    con = sqlite3.connect("data/habits.db")
    initiate_db(con)
    con.close()
    yield

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")   


@app.get("/")
async def root():
    return {"Message": "Habit Tracker"}

@app.get("/completed")
def get_completed():
    con = sqlite3.connect("data/habits.db")
    result = get_completed_db(con)
    con.close()
    return result


@app.get("/summary")
def summary():
    con = sqlite3.connect("data/habits.db")
    result = week_view_db(con)
    con.close()
    return result


@app.get("/week", response_class=HTMLResponse)
async def week(request: Request):
    con = sqlite3.connect("data/habits.db")
    habits_table, dates = week_view_db(con)
    con.close()
    return templates.TemplateResponse(
        request=request, name="habit_summary.html", context={"habits":habits_table, "dates":dates}
    )

@app.post("/add", response_class=RedirectResponse)
async def add_habit(name: Annotated[str, Form()]):
    con = sqlite3.connect("data/habits.db")
    add_habit_db(con, name)
    con.close()
    return RedirectResponse(
    "/week", status_code=303
    )

@app.post("/delete", response_class=RedirectResponse)
async def delete_habit(name: Annotated[str, Form()]):
    con = sqlite3.connect("data/habits.db")
    delete_habit_db(con, name)
    con.close()
    return RedirectResponse(
    "/week", status_code=303
    )

@app.post("/complete", response_class=RedirectResponse)
async def complete_habit(name: Annotated[str, Form()]):
    con = sqlite3.connect("data/habits.db")
    complete_habit_db(con, name)
    con.close()
    return RedirectResponse(
    "/week", status_code=303
    )