# ----------------------------------------------------------------------------------------------- #
# GUI part of application.
# ----------------------------------------------------------------------------------------------- #

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import dndCharacterApp.utils.io_utils as io
import dndCharacterApp.utils.rand_utils as ran
from dndCharacterApp.dndEntities.dndRace import Race as Race
from dndCharacterApp.dndEntities.character_sheet import CharacterSheet as CharacterSheet

# Function which sets the geometry of the window.
def set_window_geometry():
    # First get dimensions of the user's screen
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    # Get the x and y coordinates where the window will be painted
    x = int((screen_width / 2) - (_WINDOW_WIDTH / 2))
    y = int((screen_height / 2) - (_WINDOW_HEIGHT / 2))
    # Set the geometry using a formatted string, width, height, and x and y coords.
    win.geometry("{}x{}+{}+{}".format(_WINDOW_WIDTH, _WINDOW_HEIGHT, x, y))

# Function used to get all the current races available to the program to
# use as values in the appropriate
def set_race_values() -> ():
    race_list = list(io.get_row(1, io.RACE_FILE_PATH))
    if race_list is not None:
        race_list.insert(0, "Random")
        return tuple(race_list)
    else:
        text = "Could not locate the files needed to run the program." \
               "\nFiles maybe corrupted, deleted or the moved to a different location on " \
               "your device. " \
               "\nPlease restart or look into repair options if unsuccessful."
        change_text_area(text)
        return tuple(["Error"])

# Function of the generate button. Creates a character sheet given the input
# of the user.
def generate_character_sheet():

    level = _LEVEL_SELECT.get()
    race = _RACE_SELECT.get()
    # Get the path where the user would like to save their file at
    file = filedialog.asksaveasfile(title="Save character sheet.",
                                    filetypes=(("pdf files", "*.pdf"),))
    # If the file could be created then continue
    if file is not None:
        # Get the file path as a string and add the pdf extension if the user hasn't.
        file_path = file.name
        if not file_path.endswith(".pdf"):
            file_path += ".pdf"
    else:
        change_text_area("Please select a file name.")
        return
    # Attempt to create the character sheet.
    try:
        if race.lower() == "random" and level.lower() == "random":
            sheet = ran.completely_random_character_sheet()
        # Do not create a sheet if the race file was not properly read/found.
        elif race.lower() == "error":
            change_text_area("Cannot create a character sheet at this time."
                         "\nPlease restart the program.")
            return
        elif level.lower() == "random":
            level = ran.random_level()
            index = _RACES.index(race)
            race = Race(index,level)
            sheet = random_sheet_attributes(level, race)
        else:
            level = int(level)
            index = _RACES.index(race)
            race = Race(index, level)
            sheet = random_sheet_attributes(level, race)

        if sheet.create_pdf(file_path):
            change_text_area("Sheet Created.")
        else:
            change_text_area("Sheet could not be created please try again.")
    # Show an exception warning if any exceptions occur during this process.
    except Exception as ex:
        ex_name = type(ex).__name__
        ex_info = ex.args
        title_text = "Exception " + ex_name + " has occurred."
        messagebox.showerror(title=title_text, message=ex_info)
        change_text_area("Please try again.")

# Function used to change the text of the text area widget.
def change_text_area(text: str):
    text_area.config(state=NORMAL)
    text_area.delete(1.0, END)
    _TEXT_BOX_TEXT.set(text)
    text_area.insert(1.0, _TEXT_BOX_TEXT.get())
    text_area.config(state=DISABLED)

# Function used to generate other random attributes not yet
# selectable for the program. A completed sheet is returned.
def random_sheet_attributes(level: int, race:Race) -> CharacterSheet:
    age = ran.random_age(race.get_max_age())
    gender = ran.random_gender()
    name = ran.random_name(race.get_racial_name_file_path(), gender)
    align = ran.random_alignment()
    bkgr = ran.random_background(align)
    ab_scores = ran.random_ability_scores()
    dnd_class = ran.random_dnd_class(level, ab_scores, race, bkgr)
    gender = ran.random_gender()
    sheet = ran.random_character_sheet(dnd_class, gender, name, age)
    return sheet

def create_window():
    win.mainloop()

# Set GUI attributes of the frame.
win = Tk()
_WINDOW_HEIGHT = 700
_WINDOW_WIDTH = 700
_TEXT_BOX_HEIGHT = int(_WINDOW_HEIGHT / 65)
_TEXT_BOX_WIDTH = int(_WINDOW_WIDTH / 10)
text_area = Text(win,
                 height=_TEXT_BOX_HEIGHT,
                 width=_TEXT_BOX_WIDTH,
                 wrap=WORD
                 )
_TEXT = "Program is able to generate a limited amount of characters from a pool of two classes, " \
        "which each have two archtypes it can select from. (Cleric and Rogue)" \
        "\nOnly Race available is Aasimar with 10 subraces." \
        "\nBackgrounds from A-S are available as long as the background does not grant extra spells." \
        "\nFeats not available yet and only level and race can be manually selected at the moment." \
        "\nFirst Python Build. Testing to see if it works on other devices."
_TEXT_BOX_TEXT = tk.StringVar(win)
_TEXT_BOX_TEXT.set(_TEXT)
_LEVELS = ("Random", "1", "2", "3", "4", "5", "6", "7", "8",
			"9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20")
_LEVEL_SELECT = tk.StringVar(win)
_LEVEL_SELECT.set(_LEVELS[0])
_RACES = None
_RACE_SELECT = tk.StringVar(win)

# Window settings
win.title("Random Dnd Sheet Application: Build 1(Python) - 8/11/2022")
set_window_geometry()
win.columnconfigure(0, weight=1)

# Top frame settings
frame = ttk.Frame(win)
frame.grid()

# Title Label settings
title_label = ttk.Label(frame,
                       text="Random Dnd Sheet App",
                       font=("Arial", 30, 'bold')
                       )
title_label.grid(column=0,row=0, pady=(20,10))

# Feature Label settings
feature_label = ttk.Label(frame,
                          text="Features Available :",
                          font=("Arial", 20, 'italic'))
feature_label.grid(column=0,row=1, pady=25)

# Text Area settings
text_area = Text(win,
                 height=_TEXT_BOX_HEIGHT,
                 width=_TEXT_BOX_WIDTH,
                 wrap=WORD
                 )
text_area.insert(1.0, _TEXT_BOX_TEXT.get())
text_area.config(state=DISABLED)
text_area.grid(column=0,row=2, pady=10)

# Frame 2 settings
frame2 = ttk.Frame(win)
frame2.grid()

# Level selection label and drop down list settings
level_select_label = ttk.Label(frame2,
                          text="Level of Character :",
                          font=("Arial", 15))
level_select_label.grid(column=0,row=0, padx=(65, 180), pady=(50,0))
level_select_ddbox = ttk.Combobox(frame2, textvariable=_LEVEL_SELECT,
                                  font=("Arial", 12))
level_select_ddbox['values'] = _LEVELS
level_select_ddbox.grid(column=1,row=0, padx=(0, 75), pady=(50,0))

# Race selection label and drop down list settings
race_select_label = ttk.Label(frame2,
                          text="Race of Character :",
                          font=("Arial", 15))
race_select_label.grid(column=0,row=1,padx=(0,112), pady=(50,0))
_RACES = set_race_values()
_RACE_SELECT.set(_RACES[0])
race_select_ddbox = ttk.Combobox(frame2, textvariable=_RACE_SELECT,
                                  font=("Arial", 12))
race_select_ddbox['values'] = _RACES
race_select_ddbox.grid(column=1,row=1, padx=(0,75), pady=(50,0))

# Generate character label and button settings
generate_character_label = ttk.Label(frame2,
                          text="Generate Random Character :",
                          font=("Arial", 15))
generate_character_label.grid(column=0,row=2,padx=(0,28), pady=(50,0))

gen_button = Button(frame2,
                    text="Generate",
                    font=("Arial", 15),
                    command=generate_character_sheet)
gen_button.grid(column=1,row=2, padx=(0,75), pady=(50,0))

