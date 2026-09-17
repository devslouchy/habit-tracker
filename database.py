import sqlite3
import datetime



def initiate_db(connection):
    cur = connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits
        (ID integer primary key,
        name text UNIQUE COLLATE NOCASE);
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS completed
        (ID integer primary key,
        habitID integer,
        date text,
        UNIQUE(habitID, date),
        FOREIGN KEY(habitID)
            REFERENCES habits(ID))
        """)



def add_habit_db(connection, name):
    cur = connection.cursor()
    try:
        cur.execute("INSERT INTO habits (name) VALUES(?)", (name,))
        connection.commit()
    except sqlite3.IntegrityError:
        print("This is not a unique habit. Please add another")
    
def complete_habit_db(connection, name):
    cur = connection.cursor()
    cur.execute("SELECT ID FROM habits WHERE name = ?", (name,))
    result = cur.fetchone()
    if result is None :
        print("This habit does not exist, please select another")
        return 
    try:
        cur.execute("INSERT INTO completed (habitID, date) VALUES (?,date('now'))", (result[0],))
        connection.commit()
    except sqlite3.IntegrityError:
            print("This habit has already been completed today.")
              
    

def delete_habit_db(connection, name):
    cur = connection.cursor()
    cur.execute("DELETE FROM habits WHERE name = ?", (name,))
    if cur.rowcount == 1:
        print("Habit " + name + " has been deleted.")
    else:
        print("No relevant habit found")
    connection.commit()

def get_habits_db(connection):
    cur = connection.cursor()
    cur.execute("SELECT * FROM habits;")
    full_results = cur.fetchall()
    return full_results

def get_completed_db(connection):
     cur = connection.cursor()
     cur.execute("SELECT habits.name, completed.date FROM habits LEFT JOIN completed ON habits.ID = completed.habitID AND completed.date = date('now')")
     results = cur.fetchall()
     return results

def calc_stats_db(connection):
     cur = connection.cursor()
     cur.execute("SELECT COUNT(*) FROM habits;")
     total = cur.fetchone()[0]
     cur.execute("SELECT COUNT(*) FROM habits LEFT JOIN completed WHERE habits.ID = completed.habitID AND completed.date = date('now');")
     completed = cur.fetchone()[0]
     if total == 0:
        percentage = 0
        return  percentage, total, completed
     else : 
         percentage = round(completed/total*100, 2)
         return percentage, total, completed


def get_all_completed_db(connection):
    cur = connection.cursor()
    cur.execute("SELECT name, completed.date FROM habits LEFT JOIN completed ON habits.ID = completed.habitID AND completed.date BETWEEN date('now', '-6 days') AND date('now')")
    result = cur.fetchall()
    return result


def get_test_db(connection):
    cur = connection.cursor()
    cur.execute("SELECT name, completed.date FROM habits LEFT JOIN completed ON habits.ID = completed.habitID AND completed.date BETWEEN date('now', '-6 days') AND date('now')")
    result = cur.fetchall()
    return result

def week_view_db(connection):
    cur = connection.cursor()
    cur.execute("SELECT name FROM habits")
    results = cur.fetchall()
    dic = {}
    for result in results:
        dic.update({result[0] : [False,False,False,False,False,False,False]})

    dates = []
    today = datetime.date.today()
    for n in range(0,7):
        x = datetime.timedelta(days = n)
        dates.append(today - x)
    completed = get_all_completed_db(connection)

    for row in completed:
        if row[1] is not None:
            habit = row[0]
            i = dates.index(datetime.date.fromisoformat(row[1]))
            dic[habit][i] = True
    date_use = []
    for date in dates:
        date_use.append(date.strftime("%a %d"))


    return dic, date_use
    
    