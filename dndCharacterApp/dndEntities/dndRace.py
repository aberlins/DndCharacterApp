# ----------------------------------------------------------------------------------------------- #
# Class meant to represent a Race from Dnd.
# Contains: race's name, their size, casting ability (if they get racial spells),
#           languages, features, armor proficiencies, weapon proficiencies, tool proficiencies
#           ability score increases, speed, max age, and list of spells (if they get any)
# ----------------------------------------------------------------------------------------------- #

import dndCharacterApp.utils.io_utils as io


class Race:

    # Constructor for Race
    # Index for race corresponds with entries in race file
    # Level is need to add certain attributes
    def __init__(self, index_of_race: int, level: int):
        attributes = io.get_col(index_of_race, io.RACE_FILE_PATH, False)
        if attributes is not None:
            self._set_race_attributes(attributes, level)
        self._level = level

    # Function sets the attributes of the race
    def _set_race_attributes(self, attributes: (), level: int):
        self._name = attributes[0]

        # Set ability scores
        line = attributes[1].split("=")
        self._ability_score_incr = []
        for score in line:
            self._ability_score_incr.append(int(score))
        self._ability_score_incr = tuple(self._ability_score_incr)

        # If race gets racial spells set those, else set to None
        if attributes[2].lower() != "none":
            self._set_racial_spells(attributes[2], level)
        else:
            self._casting_ability = None
            self._spells = None

        line = attributes[3].split("=")
        self._features = tuple(line.copy())

        self._max_age = attributes[4]
        self._size = attributes[5]
        self._speed = attributes[6]

        line = attributes[7].split("=")
        self._languages = tuple(line.copy())

        self._racial_name_file_path = attributes[8]

        self._armor_prof = None
        self._weapon_prof = None
        self._tool_prof = None

    def _set_racial_spells(self, spellList: str, level: int):
        line = spellList.split("=")
        # First entry is casting ability
        self._casting_ability = line[0]

        # Fill spell list
        self._spells = []
        for i in range(1, len(line)):
            inner_line = line[i].split("/")
            # If the character's level is great enough, then add the spell to the list
            if level >= int(inner_line[0]):
                self._spells.append(inner_line[1])
            else:
                break
        # Convert to tuple since spells won't need further altering
        self._spells = tuple(self._spells)

    # List of getters for all attributes of the race class.
    def get_name(self) -> str:
        return self._name

    def get_level(self) -> int:
        return self._level

    def get_ability_score_incr(self):
        return tuple(self._ability_score_incr)

    def get_features(self) -> []:
        return self._features

    def get_max_age(self) -> int:
        return self._max_age

    def get_size(self) -> str:
        return self._size

    def get_speed(self) -> int:
        return self._speed

    def get_languages(self) -> ():
        return self._languages

    def get_racial_name_file_path(self) -> str:
        return self._racial_name_file_path

    def get_casting_ability(self) -> str:
        return self._casting_ability

    def get_spells(self) -> []:
        return self._spells

    def get_armor_prof(self) -> ():
        return self._armor_prof

    def get_weapon_prof(self) -> ():
        return self._weapon_prof

    def get_tool_prof(self) -> ():
        return self._tool_prof
