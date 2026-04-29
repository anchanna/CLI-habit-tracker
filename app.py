import sys
import os
import csv
import re
import bcrypt
from datetime import date,timedelta,datetime
import json
from tabulate import tabulate
from termcolor import colored
from terminaltexteffects.effects.effect_rain import Rain

class User:
    def __init__(self,mail_id,habits):
        self._mail_id = mail_id
        self.file_name = f"{mail_id.replace('@','_').replace('.','_')}.json"
        self.habits = habits


    def save(self):
        data = {"email":self._mail_id,
                "habits":self.habits}
        with open(self.file_name,"w") as f:
            json.dump(data,f,indent=4)


    def add_habits(self):
        while True:
            habit_ip = input("\nenter the habit: ").strip().lower()
            if not habit_ip or habit_ip.isspace():
                print(colored("enter some name for the habit ","magenta"))
            else:
                already_exists = False
                for habit in self.habits:
                    if habit["name"] == habit_ip:
                        already_exists = True
                        break

                if already_exists:
                    print(colored("the habit already exists.","magenta"))
                else:
                    firstday = str(date.today() - timedelta(days=1))
                    habit = {"name": habit_ip,
                            "status":0,
                            "streak":0,
                            "last_completed":firstday}
                    self.habits.append(habit)
                    self.save()
                    print(colored("habit is successfully added ☺️ ✨","green"))
                    return



    def status_update(self):

        if not self.habits:
            print(colored("You have no habits yet. Please add one first","magenta"))
            return
        while True:
            print("\nhabits:")
            for habit in self.habits:
                print(habit["name"])
            habit = input("\nenter the habit u want to change the status for: ").strip().lower()
            if not habit:
                print(colored("enter something please","magenta"))
            else:
                found = False
                for h in self.habits:
                    if h["name"] == habit:
                        found = True
                        print("current status: ")
                        print(json.dumps(h,indent=4))
                        while True:
                            try:
                                ans = int(input("\ndo u want to change the status? :\n"
                                    "1. YES\n"
                                    "2. NO\n"
                                    "enter 1 OR 2: \n"))

                                if ans == 1:
                                    if h["status"] == 0:
                                        h["status"] = 1
                                        print(colored("\n----status changed successfully----","green"))
                                        last_date = datetime.strptime(h["last_completed"],"%Y-%m-%d").date()
                                        today = date.today()
                                        delta = (today - last_date).days
                                        if delta == 1:
                                            h["streak"] += 1
                                        else:
                                            h["streak"] = 1
                                        h["last_completed"] = str(today)

                                        a = h["streak"]
                                        if a % 7 == 0:
                                            text = (f"\n🎉congratulations you have achieved streak for a week {a} days in {h['name']}🎉\n").upper()
                                            rain = Rain(text)
                                            with rain.terminal_output() as terminal:
                                                for frame in rain:
                                                    terminal.print(frame)

                                        self.save()
                                        return

                                    elif h["status"] == 1:
                                        h["status"] = 0
                                        print(colored("----status changed----","green"))
                                        h["streak"] -= 1
                                        h["last_completed"] = str(date.today() - timedelta(days=1))
                                        self.save()
                                        return

                                elif ans == 2:
                                    print("no changes is made in status")
                                    return

                            except  ValueError:
                                print(colored("selection required. give a proper anwser. only enter 1 or 2 according to ur answer","red"))
                                pass

                if not found:
                    print(colored(f"\nCould not find a habit named '{habit}'","magenta"))


    def view_habits(self):

        if not self.habits:
            print(colored("\nNo habits found. Start by adding one","magenta"))
            return

        header = ["Habit Name", "Status", "Streak", "Last Completed"]
        data = []
        for d in self.habits:
            if d["status"] == 0:
                statushere = "not yet completed"
            elif d["status"] == 1:
                statushere = "completed"
            data.append([d["name"],statushere,d["streak"],d["last_completed"]])
        table=tabulate(data, headers = header , tablefmt= "grid")
        print("\n------------DASHBOARD------------")
        print(f"\n{self._mail_id}")
        print()
        print(table)

    def delete_habit(self):
        while True:
            print("\nwhich habit do u wanna delete?")
            for habit in self.habits:
                print(habit["name"])

            ans = input("\nenter the name of the habit: ").strip().lower()
            if not ans:
                print(colored("enter some name for the habit ","magenta"))
            else:
                found = False
                for h in self.habits:
                    if h["name"] == ans:
                        found = True
                        while True:
                            con = input("are u sure u want to delete? enter Y/N accordingly : ").strip().upper()
                            if not con:
                                print(colored("\nselection required. please enter Y OR N\n","magenta"))
                            else:
                                if con in ["Y","N"]:
                                    if con == "Y":
                                        self.habits.remove(h)
                                        print(colored("\nhabit successfully deleted","green"))
                                        self.save()
                                        self.view_habits()
                                        return

                                    elif con == "N":
                                        print(colored("habit is not deleted","magenta"))
                                        break
                                else:
                                    print(colored("only enter Y or N accordingly","red"))

                if not found:
                    print(colored("habit cant be found. enter the name properly","red"))


    def daily_reset(self):

        today = date.today()
        changed = False

        for h in self.habits:
            last_date = datetime.strptime(h["last_completed"],"%Y-%m-%d").date()
            if last_date != today:
                h["status"] = 0
                changed = True

            delta = (today - last_date).days
            if delta > 1:
                h["streak"] = 0
                changed = True

        if changed:
            self.save()



def authenticate_user(email,option):
    with open("users.json")as file:
        file1 = json.load(file)
        if email in file1:
            if option == 1:
                status,habits = login(email)
                return status,habits
            elif option == 2:
                print("\nthe account already exists\n""continue by logging in\n")
                status,habits = login(email)
                return status,habits

        if email not in file1:
            if option == 1:
                print(colored("\nthe account doesn't exist.\n"
                    "start by completing the process of creating this account","magenta"))
                while True:
                    ans = input("\ncontinue creating this account? Y/N: ").strip().upper()
                    if not ans:
                        print(colored("/nselection required. please enter Y or N/n","magenta"))
                    else:
                        if ans in ["Y","N"]:
                            if ans == "Y":
                                status,habits = signup(email)
                                return status,habits
                            elif ans == "N":
                                status = 0
                                habits = []
                                return status,habits
                        else:
                            print(colored("\nonly enter Y or N accordingly","red"))

            elif option == 2:
                status,habits = signup(email)
                return status,habits



def login(email):
    with open("users.json", "r") as f:
        data = json.load(f)
    times = 1
    while times <= 3:

        password = input("enter password: ").strip()
        if not password:
            print(colored("enter something for the password","magenta"))
            continue

        else:
            userBytes = password.encode('utf-8')
            passwordd = data[email]["password"]
            hash = passwordd.encode('utf-8')
            result = bcrypt.checkpw(userBytes, hash)
            if result:
                print(colored("\nlogin successful!","green"))
                status = 1
                # habits = []
                filen= filename(email)
                filej= f"{filen}.json"
                with open(filej,"r") as fl:
                    d = json.load(fl)
                    habits = d["habits"]
                return status,habits
            else:
                times += 1
                if times <= 3:
                    print(colored("you have entered wrong password. try again","magenta"))


    if times > 3:
        print(colored("u have entered wrong password many times","red"))
        status = 0
        habits = []
        return status,habits


def filename(email):
    name = email.replace("@","_").replace(".","_")
    return name

def signup(email):

    with open("users.json", "r") as f:
        data = json.load(f)
    email = email
    password = validate_password()
    name=filename(email)
    data[email] = {"password": password,"file": name+'.json'}
    with open("users.json","w")as file:
        json.dump(data, file)
    print(colored("Signup successful!","green"))
    status = 1
    namee = name+".json"
    with open(namee,"w")as data:
        d = {"email":email,
                "habits":[] }
        json.dump(d,data,indent=4)
    habits = []
    return status,habits

def check_email(email):
    matches = re.search(r"^[a-zA-Z0-9.!#$%&'*+\/=?^_{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$", email)
    return bool(matches)

def validate_email():
    while True:
        email = input("\nenter your email ID: ").strip()
        if not email:
            print(colored("section required. please enter your email ID.","red"))
        else:
            if check_email(email):
                return email
            else:
                print(colored("\nenter valid mail id","red"))

def check_password(password):
    match = re.search(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,20}$", password)
    return bool(match)

def validate_password():
    while True:
        password = input("enter password: ").strip()
        if check_password(password):

            pass_bytes = password.encode('utf-8')
            # generating the salt
            salt = bcrypt.gensalt()

            # Hashing the password
            hash = bcrypt.hashpw(pass_bytes, salt)

            while True:
                repassword = input("re-enter password: ").strip()
                if not repassword:
                    print("section required. please re-enter your password")
                else:
                    userBytes = repassword.encode('utf-8')
                    result = bcrypt.checkpw(userBytes, hash)
                    if not result:
                        print(colored("password doesn't match","red"))
                    else:
                        hash_to_store = hash.decode('utf-8')
                        return hash_to_store

        else:
            print(colored("\nthe password must contain \n"
                    "8 to 20 characters in length\n"
                    "containing at least one uppercase letter & one lowercase letter\n"
                    "one digit & one special character from the set !@#$%^&*\n", "red"))


def main():

    file_path = "users.json"
    if not os.path.isfile(file_path):
        with open("users.json", "w") as f:
            d = {}
            json.dump(d,f,indent=4)

    status = 0
    print(str.upper("\n------------------------welcome to the HABIT TRACKER------------------------\n"))
    while True:
        try:
            print("\n--------NOTE: use ctrl + D to come back to this menu--------")
            option=int(input("\nselect your option by mentioning the number (ex: 2)\n"
                            "1.login\n"
                            "2.signup\n"
                            "3.exit\n"))
            if option == 1 or option == 2 :
                email = validate_email()
                status, habits = authenticate_user(email,option)
            elif option == 3:
                sys.exit()

        except ValueError:
            print(colored("\nselection required. only enter numbers according to the functionality u want","red"))
            continue

        except EOFError:
            print(colored("\nReturning to menu...", "green"))
            pass


        if status != 0:
            active_user = User(email,habits)
            active_user.daily_reset()


        while status != 0:
            try:
                print("\n--------------NOTE: use ctrl + D to come back to this menu--------------")
                option1=int(input("\nselect your option by mentioning the number (ex: 2)\n"
                            "1.add habit\n"
                            "2.update status of habit\n"
                            "3.view habits\n"
                            "4.delete a habit\n"
                            "5.logout\n"))
                if option1 in [1,2,3,4,5]:
                    if option1 == 1:
                        active_user.add_habits()
                    elif option1 == 2:
                        active_user.status_update()
                    elif option1 == 3:
                        active_user.view_habits()
                    elif option1 == 4:
                        active_user.delete_habit()
                    elif option1 == 5:
                        print(colored("--logged out--","green"))
                        status = 0
                else:
                    print(colored("\nonly enter number from 1 to 5 accordingly","red"))

            except ValueError:
                print(colored("\nselection required. only enter numbers according to the functionality u want","red"))

            except EOFError:
                print(colored("\nReturning to menu...", "green"))
                pass

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print(colored("program ending","green"))
        sys.exit()


