# Quester's Cache (CITS3403-project)
Group project for building a request forum application

# Project Description
An RPG-themed quest board where users can post ReQuests for other users to take on and complete!

ReQuest responses must be validated before awarding valuable gold to the adventurer!

Take on other adventurers on the leaderboard as you race to the top to have the most gold done!

# Credits
| UWA ID       | Name           | GitHub Username       |
|----------|----------------|----------------|
| 22874102 | Brendan Tan    | Blizzerac      |
| 23374198 | Stefan Andonov | stef-andonov   |
| 23616029 | Kyle Dunstall  | UpstandingVlad |
| 23340022 | Cameron O'Neill| keyman015      |

# Launch Instructions
Before launching the application, there are several packages and installations required.

To begin, ensure that there is a python3 and pip3 installation present. These can be installed with:

sudo apt install python3 python3-pip

Next, create a virtual environment. If you do not have virtualenv, it can be installed with:

pip install virtualenv

Navigate to the deliverables folder and install the required packages with:

pip install -r requirements.txt

Initialise a database with:

flask db init

Finally, navigate to the src directory and run the application with:

flask run

# Test Instructions 

Navigate to the src directory and open QuesterCache.py file. Comment out the deployment configuration, allowing the testing database configuration to be used.

From the same directory, run unit tests with:

python -m unittest tests/unit.py

Run selenium tests with:

python -m unittest tests/selenium.py (cannot be done in WSL)

## Languages and Frameworks Used
- HTML
- CSS
- JavaScript
- Python
---
- Bootstrap
- Flask
- JQuery
- AJAX
- SQLite
