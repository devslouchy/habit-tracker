from database import get_habits_db, add_habit_db, complete_habit_db, delete_habit_db, calc_stats_db, get_completed_db, initiate_db, get_all_completed_db
import sqlite3


con = sqlite3.connect("data/habits.db")

initiate_db(con)

def main_menu() : 
	running = True
	while running : 
		print("""
		---HABIT TRACKER---
		
		1. Add habit
		2. Complete Habit
		3. Remove habit
		4. Show Habits
		5. Show Statistics
		6. Quit
		
		""")
		selection = input("Choose an option :").strip()
		if selection == "1" : 
			habit = input("What is the new habit? : ").strip()
			add_habit_db(con, habit)
		elif selection == "2" : 
			completed = input("Which habit would you like to complete? : ").strip()
			complete_habit_db(con, completed)
		elif selection == "3" :
			delete = input("Which habit would you like to delete? : ").strip()
			delete_habit_db(con, delete)
		elif selection == "4" :
			print_habits()
		elif selection == "5" :
			print_stats()
		elif selection == "6" : 
			print("Thank you for using the Habit Tracker, goodbye!")
			running = False
		elif selection == "7":
			print(str(get_all_completed_db(con)))
		else : 
			print("Please enter a valid option from the menu")
		

def print_stats():
	(percentage, total, completed) = calc_stats_db(con)
	if total == 0:
		print("You have no habits to view statistics on.")
	else : 
		print("Your total habits are : " + str(total))
		print("Your total completed habits are :" + str(completed))
		print("The percentage of complete habits are : " + str(percentage) + "%")

def print_habits():
	for result in get_completed_db(con) :
		if result[1] is None :
			print(result[0] + "-> Incomplete")
		else : 
			print(result[0] + "-> Completed")
		
main_menu()
	







