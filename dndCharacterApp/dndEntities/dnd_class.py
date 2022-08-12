# ----------------------------------------------------------------------------------------------- #
# Class meant to represent a Class from Dnd.
# Contains: class's name, hit die, proficiency bonus, level, initiative, armors,
#           weapons, items, features, languages, attacks and spells, ability scores,
#           archetype name, saving throws and proficiencies for armors, weapons and tools
# ----------------------------------------------------------------------------------------------- #

from dndCharacterApp.dndEntities.dndRace import Race as Race
from dndCharacterApp.dndEntities.dndBackground import Background as Background
import dndCharacterApp.utils.io_utils as io
import dndCharacterApp.utils.math_utils as math

class DndClass:

    # Constructor for DndClass
    # Name for class corresponds with entries in class file
    # Level and ability scores is need to add certain attributes
    # Race and background are provided for extra additions but
    # can be omitted to create an incomplete class
    def __init__(self, name: str, level: int, ability_scores: [],
                 race: Race, background: Background):
        self._name = name
        self._level = level
        self.ability_scores = ability_scores
        self._race = race
        self._background = background
        # Finialize character's ability scores if a Race is supplied.
        if self._race is not None:
            self.ability_scores = finalize_ability_scores \
                (self.ability_scores, self._race.get_ability_score_incr())
        self._initialize_standard_attributes()
        self._set_none_attributes()
        # Get list of the class's attributes that require choices for later use
        self._choice_attributes_list = io.get_col(self._name, io.CLASS_CHOICE_FILE_PATH, False)

    # Function used to set attributes of the class which are non-optional
    def _initialize_standard_attributes(self):
        line = io.get_col(self._name, io.CLASS_STAND_FILE_PATH, True)
        # Set standard attributes associated with the class
        self._prof_bonus = _get_prof_bonus(line[1].split("="), self._level)
        self._hit_die = line[2]
        self._armor_prof = line[3].split("=")
        self._weapon_prof = line[4].split("=")
        self._tool_prof = line[5].split("=")
        self._saving_throws = line[6].split("=")

        # Check to see if the class is a caster, depending on which set the
        # caster attributes thusly.
        sub_line = line[7].split("=")
        if sub_line[0].lower() == "true":
            self._initialize_spell_casting_traits(sub_line)
        else:
            self._initialize_non_spell_casting_attributes()

        # Finally set all features and attacks the character can learn at their level.
        self._features = _initialize_features_or_attacks(
            line[8].split("="), self._level)
        self._attacks_and_spell_casting = _initialize_features_or_attacks(
            line[9].split("="), self._level)

    # Function used to set spell caster attributes
    def _initialize_spell_casting_traits(self, line: []):
        self._casting_ability = line[1]
        self._spell_list_file_path = line[3]
        self._prepared_or_known = line[4].lower()[0]
        self._set_spells_and_slots(line[2])

    # Function used to set spell slots as well as an empty spell list
    def _set_spells_and_slots(self, file_path: str):
        # Get caster information
        line = io.get_col(self._level, file_path, False)
        self._spell_slots = []
        # If the caster is a known caster set the number of spells, else set it to
        # -1.
        self._spells_known = line[1] if self._prepared_or_known == "k" else -1

        # Set the number of spells for each spell level the caster may use per day.
        for i in range(2, len(line)):
            self._spell_slots.append(line[i])

        # Make a 2-D list with the maximum spell level dependent on the class's spell
        # slots for that level.
        self.spells = [[] for i in range(len(self._spell_slots))]

    # Function used to fill spell caster attributes with None values if the
    # class is a non-spell caster.
    def _initialize_non_spell_casting_attributes(self):
        self._casting_ability = None
        self._spell_list_file_path = None
        self._prepared_or_known = None
        self._spell_slots = None
        self._spells_known = None
        self.spells = None

    # Function which initializes attributes of the class which have null values
    # by default
    def _set_none_attributes(self):
        self._init_bonus = None
        self._archetype_name = None
        self._skill_bonuses = None
        self.armor = None
        self.weapons = None
        self.items = None
        self.languages = None

    # Function used to set bonus attributes to the class granted by the
    # selected archetype. If the archetype is granted spells and requires
    # further selection then the sender is notified.
    def set_archetype_attributes(self, file_path: str, index: int) -> bool:
        line = io.get_col(index, file_path, False)
        need_to_set_spells = False

        # Add extra bonuses and proficiencies granted by the archetype.
        if line[1].lower() != "none":
           self._armor_prof = _add_more_items_to_list(
               list(self._armor_prof), line[1].split("="))
        if line[2].lower() != "none":
            self._weapon_prof = _add_more_items_to_list(
                list(self._weapon_prof_prof), line[2].split("="))
        if line[3].lower() != "none":
            self._tool_prof = _add_more_items_to_list(
                list(self._tool_prof), line[3].split("="))
        if line[4].lower() != "none":
            _add_more_items_to_list(
                list(self._skill_bonuses), line[4].split("="))

        # Check to see if archetype grants spell casting and set traits accordingly.
        sub_line = line[6].split("=")
        if sub_line[0].lower() == "true":
            self._initialize_spell_casting_traits(sub_line)

        # Check to see if archetype grants bonus spells and add them accordingly
        # If further spell selection is needed notify the sender.
        sub_line = line[5].split("=")
        if sub_line[0].lower() == "true":
            need_to_set_spells = self._set_bonus_spells(sub_line[1])

        # Add new features gained through the archetype to the final list.
        new_features = _initialize_features_or_attacks(line[7].split("="), self._level)
        self._features = _add_more_items_to_list(self._features, tuple(new_features))

        return need_to_set_spells

    # Function used to set skill bonuses only if they are valid
    # skills for the class to be proficient in.
    # True is returned if successful.
    def set_skill_bonus(self, skill_bonuses: []) -> bool:
        skill_bonus_rules = self._choice_attributes_list[1].split("=")
        # Check to see if the proper amount of skills are selected.
        if len(skill_bonuses) > int(skill_bonus_rules[0]):
            return False

        valid_skill_list = skill_bonus_rules[1].split("/")

        # Loop through the skill list checking if the master list contains them.
        for skill in skill_bonuses:
            if skill not in valid_skill_list:
                return False

        self._skill_bonuses = tuple(skill_bonuses)
        return True

    # Function used to set bonus spells granted to the class depending
    # on its level, if the class requires further selection in terms of the spells
    # granted to it, the sender is thusly notified.
    def _set_bonus_spells(self, file_path: str) -> bool:
        spell_list = []
        need_to_set_spells = False
        # Index for columns in bonus spells file
        index = 1

        # Get the bonus spells for the class/archetype
        while True:
            line = io.get_col(index, file_path, False)
            index += 1
            # If an empty list or none is returned the list is complete
            if line is not None:
                if len(line) > 0:
                    spell_list.append(line)
                else:
                    break
            else:
                break

        # Go through all the spells gained at specific levels and add them to
        # the class if they are a high enough level to obtain them.
        for entries in spell_list:
            if self._level < int(entries[0]):
                break
            # Index for spell level
            index = 0
            # Get the list of spells for that spell level at for the
            # given class level
            for i in range(1, len(entries)):
                line = entries[i].split("=")
                for sub_entries in line:
                    # Add the spell to the spell list and if further selection needs
                    # to be made notify the sender.
                    if sub_entries != "-":
                        self.spells[index].append(sub_entries)
                        if sub_entries.startswith("*"):
                            need_to_set_spells = True
                # Increase spell level once all entries of the previous are finished.
                index += 1

        # Notify the sender if the spell list is incomplete.
        return need_to_set_spells

    # Function that sets the archetype's name if no name has been set yet.
    def set_archetype_name(self, name: str) -> bool:
        if self._archetype_name is None:
            self._archetype_name = name
            return True
        return False

    # Function that sets the class's race if one is not set and the race and
    # class's levels match. A boolean is returned corresponding to if the
    # operation was successful.
    def set_race(self, race: Race) -> bool:
        if self._race is None:
            if self._level == race.get_level():
                self._race = race
                self.ability_scores = finalize_ability_scores\
                    (self.ability_scores, self._race.get_ability_score_incr())
                return True
        return False

    # Function that sets the class's background if one is not set.
    # A boolean is returned corresponding to if the operation was successful.
    def set_background(self, background: Background) -> bool:
        if self._background is None:
            self._background = background
            return True
        return False

    def set_attacks_and_spell_casting(self, attacks_and_spell_casting: ()):
        self._attacks_and_spell_casting = attacks_and_spell_casting

    # Getters for private attributes of dnd class
    def get_name(self) -> str:
        return self._name

    def get_level(self) -> int:
        return self._level

    def get_hit_die(self) -> int:
        return self._hit_die

    def get_prof_bonus(self) -> int:
        return self._prof_bonus

    def get_init_bonus(self) -> int:
        return self._init_bonus

    def get_armor_prof(self) -> ():
        return tuple(self._armor_prof)

    def get_weapon_prof(self) -> ():
        return tuple(self._weapon_prof)

    def get_tool_prof(self) -> ():
        return tuple(self._tool_prof)

    def get_saving_throws(self) -> ():
        return tuple(self._saving_throws)

    def get_attacks_and_spell_casting(self) -> ():
        return tuple(self._attacks_and_spell_casting)

    def get_casting_ability(self) -> str:
        return self._casting_ability

    def get_spell_attack_bonus(self) -> int:
        if self._casting_ability is not None:
            return math.get_spell_attack_bonus(self.ability_scores,
                                           self._casting_ability, self._prof_bonus)
        return -1

    def get_spell_save_dc(self) -> int:
        if self._casting_ability is not None:
            return math.get_spell_save_dc(self.ability_scores,
                                           self._casting_ability, self._prof_bonus)
        return -1

    def get_prepared_or_known(self) -> str:
        return self._prepared_or_known

    def get_spell_slots(self) -> ():
        return self._spell_slots

    def get_spells_known(self) -> int:
        return self._spells_known

    def get_spell_list_file_path(self) -> str:
        return self._spell_list_file_path

    def get_choice_attributes_list(self) -> ():
        return tuple(self._choice_attributes_list)

    def get_skill_bonuses(self) -> ():
        return tuple(self._skill_bonuses)

    def get_archetype_name(self) -> str:
        return self._archetype_name

    def get_features(self) -> ():
        return tuple(self._features)

    def get_race(self) -> Race:
        return self._race

    def get_background(self) -> Background:
        return self._background

# Function used to add a Race's ability modifiers to the character's final
# stats.
def finalize_ability_scores(ability_scores: [], ability_score_incr: ()) -> []:
    for i in range(6):
        # If a situation arises when adding an ability score increase
        # would make a stat above 20, just set the score to a max of 20.
        if ability_scores[i] + ability_score_incr[i] < 20:
            ability_scores[i] += ability_score_incr[i]
        else:
            ability_scores[i] = 20
    return ability_scores

def finalize_attacks_and_spell_casting(attacks_and_spell_casting: [], level: int) -> ():
    if attacks_and_spell_casting is not None:
        for i in range(len(attacks_and_spell_casting)):
            line = io.get_col(attacks_and_spell_casting[i], io.CLASS_ATT_SPELL_INCR_FILE_PATH, True)
            if line is not None:
                attacks_and_spell_casting[i] += " " + line[level]

    return attacks_and_spell_casting

# Function used to get a class's features or attacks depending on the
# class itself and the level of the character.
def _initialize_features_or_attacks(line: [], level: int) -> []:
    temp_list = []
    # Continue looping through the list until the character's level
    # is not high enough to add that feature or attack to itself
    for entries in line:
        sub_line = entries.split("/")
        if level < int(sub_line[0]):
            break
        else:
            temp_list.append(sub_line[1])
    return temp_list

# Function used to get a class's proficiency bonus depending on the
# class itself and the level of the character.
def _get_prof_bonus(line: [], level: int) -> int:
    # Search through list until the character's level is found.
    for entries in line:
        sub_line = entries.split("/")
        if int(sub_line[0]) == level:
            return int(sub_line[1])
    # Return -1 if an improper level is given.
    return -1

# Function used to add additional items to a dnd class's
# armor, weapon, tool or skill bonuses/proficiencies.
def _add_more_items_to_list(old_list: [], new_items: ()) -> ():
    for item in new_items:
        old_list.append(item)
    return old_list


