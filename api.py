from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import get_completed_db, get_test_db, week_view_db
import sqlite3

app = FastAPI()
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

@app.get("/testing")
def testing():
    con = sqlite3.connect("data/habits.db")
    result = get_test_db(con)
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