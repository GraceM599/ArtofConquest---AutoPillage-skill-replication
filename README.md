
#### Overview
The AutoPillage skill replicator is a Python bot that uses OpenCV to replicate the capabilities of the Auto Pillage skill obtained by purchasing lifetime patron. It leverages:
  - Screen capture of a possibly scaled BlueStacks window
  - Template matching to exclamation marks above unused dungeons/resources with OpenCV.
  - Automation of mouse clicks using `pyautogui`

This lets players without lifetime patron save time in their daily tasks and during events.

#### Features
Detects and interacts with game UI elements.
Template matching to locate buttons and indicators.
Readjusts the window and scales coordinates to operate on scaled monitors.
Can be used to reduce the focus required during extremly repetative events like Golem Invasion by template matching the golems and repeating a similar process to dungeon clearning with them.

#### Usage
Clone the repository, create and activate a virtual enviroment, and install the dpeendencies located in requirements.txt. 
Ensure BlueStacks is open and visible on the screen (not behind another window) and run the script.

To extend functionality to other enemies/tasks use the 'getScreenshots()' function to collect screenshots of the game to act as templates and the 'tester()' function to test if the template is detectable. 


#### File Structure
ArtofConquest---AutoPillage-skill-replication/
├── images/               # Screenshots and templates
├── AOCbot.py             # Main script
├── requirements.txt      # Python dependencies
└── README.md               


#### Disclaimer
This project is intended for **educational purposes only**. It demonstrates using OpenCV for simple template matching and pyautogui for automating user input. 
