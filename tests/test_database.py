from database import initiate_db, add_habit_db, complete_habit_db, delete_habit_db, get_completed_db, calc_stats_db
import sqlite3
import os
import pytest


@pytest.fixture
def test_db():
    con = sqlite3.connect("testing.db")
    initiate_db(con)

    yield con

    con.close()
    os.remove("./testing.db")

def test_add_habit(test_db):
    cur = test_db.cursor()
    add_habit_db(test_db, "Run")
    cur.execute("SELECT * FROM habits WHERE name ='Run'")
    result =  cur.fetchone()
    assert result == (1, "Run")

def test_unique_habits(test_db):
    cur = test_db.cursor()
    add_habit_db(test_db, "Run")
    add_habit_db(test_db, "run")
    cur.execute("SELECT COUNT(*) FROM habits WHERE name ='Run' or 'run'")
    result = cur.fetchone()[0]
    assert result ==  1  

def test_complete_habit(test_db):
    cur = test_db.cursor()
    add_habit_db(test_db, "Run")
    complete_habit_db(test_db, "Run")
    cur.execute("SELECT COUNT(*) FROM completed WHERE completed.habitID = 1")
    result = cur.fetchone()[0]
    assert result == 1


def test_duplicate_complete_habit(test_db):
    cur = test_db.cursor()
    add_habit_db(test_db, "Run")
    complete_habit_db(test_db, "Run")
    complete_habit_db(test_db, "Run")
    cur.execute("SELECT COUNT(*) FROM completed WHERE completed.habitID = 1")
    result = cur.fetchone()[0]
    assert result == 1


def test_complete_not_habit(test_db):
    cur = test_db.cursor()
    complete_habit_db(test_db, "Run")
    cur.execute("SELECT COUNT(*) FROM completed WHERE completed.habitID = 1")
    result = cur.fetchone()[0]
    assert result == 0

def test_delete_habit(test_db):
    cur = test_db.cursor()
    add_habit_db(test_db, "Run")
    delete_habit_db(test_db, "Run")
    cur.execute("SELECT * FROM habits WHERE name ='Run'")
    result = cur.fetchall()
    assert result == []

def test_delete_not_habit(test_db):
    cur = test_db.cursor()
    delete_habit_db(test_db, "Run")
    cur.execute("SELECT * FROM habits")
    result = cur.fetchall()
    assert result == []

def test_get_completed(test_db):
    add_habit_db(test_db, "Run")
    add_habit_db(test_db, "Read")
    complete_habit_db(test_db, "Run")
    result = get_completed_db(test_db)
    assert result[0][0] == "Run"
    assert result[0][1] is not None
    assert result[1][0] == "Read"
    assert result[1][1] is None

def test_calc_stats_empty(test_db):
    result = calc_stats_db(test_db)
    assert result == (0,0,0)

def test_calc_stats_completed(test_db):
    add_habit_db(test_db, "Run")
    add_habit_db(test_db, "Read")
    complete_habit_db(test_db, "Run")
    result = calc_stats_db(test_db)
    assert result == (50.0, 2, 1)
                       
