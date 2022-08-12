# ----------------------------------------------------------------------------------------------- #
# Class meant to represent a Background from Dnd.
# Contains: background's name, their alignment, skill proficiency, tool proficiency,
#           languages, equipment, money, features, personality trait, ideal, bonds, and
#           flaw.
# ----------------------------------------------------------------------------------------------- #
from dndCharacterApp.dndEntities.dnd_enums import Alignment as Alignment
import dndCharacterApp.utils.io_utils as io


class Background:

    # Constructor for Race
    # Index for background corresponds with entries in background file
    # Alignment is need to add certain attributes
    def __init__(self, alignment: Alignment, background_index: int):
        self._alignment = alignment
        self._index = background_index
        self._ideals_list = \
            io.get_col(background_index, io.BKGR_IDEALS_FILE_PATH, False) \
                if background_index != -1 else None
        self._initialize_attributes()
        self._set_none_attributes()

    # Function sets the attributes of the background
    def _initialize_attributes(self):
        if self._index != -1:
            line = io.get_col(self._index, io.BKGR_ATRBT_FILE_PATH, False)
            self.name = line[0]
            self._skill_prof = line[1].split("=")
            self.tool_prof = line[2].split("=")
            self.languages = line[3].split("=")
            self.equipment = line[4].split("=")
            self._money = _initialize_money(list(line[5].split("=")))
            self._features = line[6].split("=")

    # Function which initializes attributes of the background which have null values
    # by default
    def _set_none_attributes(self):
        self.personality_trait = None
        self._ideal = None
        self.bond = None
        self.flaw = None

    # Function which sets the background's ideal based on its given alignment
    # Index is used to choose from the background's ideal list.
    # A boolean value is returned whether or not this operation was successful
    def set_ideal(self, ideal_index: int) -> bool:
        # If the ideal list was properly set
        if self._ideals_list is not None:
            # Split between alignments which can get this ideal and its description
            selected_ideal = self._ideals_list[ideal_index].split("=")
            # If the alignment is any or the GE/LC matches the alignment set the ideal
            # as such.
            if selected_ideal[0].lower() == "any" or \
                    self._alignment.ge_axis_value().lower() == selected_ideal[0].lower() or \
                    self._alignment.lc_axis_value().lower() == selected_ideal[0].lower():
                self._ideal = selected_ideal[1]
                return True
        return False

    # Getters for attributes of the background class that can not be changed
    def get_ideal(self) -> str:
        return self._ideal
    def get_ideals_list(self) -> ():
        return tuple(self._ideals_list)
    def get_money(self) -> []:
        return self._money
    def get_skill_prof(self) -> ():
        return tuple(self._skill_prof)
    def get_features(self) -> ():
        return tuple(self._features)
    def get_alignment(self) -> Alignment:
        return self._alignment
    def get_index(self) -> int:
        return self._index

# Private function used to set money of a background
# List passed in should have the second value be the type of
# money (gold, copper, etc.) and first value should be numeric amount.
def _initialize_money(money: []) -> []:
    # All values are 0
    final_money = [0 for i in range(5)]
    index = 0
    # Second value in money list represents type of money
    match (money[1][0]):
        # Copper
        case "C":
            index = 0
        # Silver
        case "S":
            index = 1
        # Electrum
        case "E":
            index = 2
        # Gold
        case "G":
            index = 3
        # Platinum
        case "P":
            index = 4
        # If the string isn't formatted right return 0s for all money
        case _:
            return final_money
    final_money[index] = int(money[0])
    return final_money

