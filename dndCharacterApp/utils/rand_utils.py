# ----------------------------------------------------------------------------------------------- #
# Module which contains methods for producing random attributes of a dnd character;
# level, stats, race, class, etc.
# ----------------------------------------------------------------------------------------------- #

import random
import dndCharacterApp.utils.math_utils as math_utils
import dndCharacterApp.utils.io_utils as io
import dndCharacterApp.dndEntities.dnd_class as dnd_mod
from dndCharacterApp.dndEntities.dnd_enums import Alignment as Alignment
from dndCharacterApp.dndEntities.dnd_enums import Gender as Gender
from dndCharacterApp.dndEntities.dndRace import Race as Race
from dndCharacterApp.dndEntities.dndBackground import Background as Background
from dndCharacterApp.dndEntities.dnd_class import DndClass as DndClass
from dndCharacterApp.dndEntities.character_sheet import CharacterSheet as CharacterSheet

# Function used to return a random level between 1-20
def random_level() -> int:
    return random.randint(1, 20)

# Function used to roll up a set of six ability scores, each roll is random as if using a d6.
# Can either roll completely randomly or use a point by system with random points attached to
# each ability score.
# List has ability scores as follows: Str, Dex, Con, Int, Wis and Cha
def random_ability_scores(point_by=False) -> []:
    ability_scores = []

    # Point by System:
    if point_by:
        # Begin with 27 points
        points = 27
        # Each score is set to a default 8
        ability_scores = [8 for i in range(6)]
        while points > 0:
            # Get random ability score
            index = random.randint(0, 5)
            # If the ability score is not at its max (15) then add to it
            if ability_scores[index] < 15:
                # 9-13 costs one point to increase
                if ability_scores[index] < 13:
                    ability_scores[index] += 1
                    points -= 1
                # 14-15 costs 2 points to increase
                else:
                    ability_scores[index] += 1
                    points -= 2
    # Completely Random Rolls:
    else:
        # Roll for each of the 6 stats
        for i in range(6):
            # Roll 4 times and then add up the 3 highest rolls as the ability score
            temp_rolls = []
            for j in range(4):
                temp_rolls.append(random.randint(1, 6))
            temp_rolls.sort(reverse=True)
            ability_scores.append(temp_rolls[0] + temp_rolls[1] + temp_rolls[2])

    return ability_scores

# Function used to increase a set of ability scores given a level and the ability scores
# themselves. At levels 4, 8, 12, 16, and 19 ability scores can be increased; either
# increasing one score by 2 points or two scores by 1 point. No score can exceed 20.
def random_ability_scores_improve(level: int, ability_scores: []) -> []:
    # Continue while the level has not been decremented to 0.
    while True:
        # If the score is 4, 8, 12, 16 or 19 increase it
        if (level == 19) or (level % 4 == 0 and level != 0 and level != 20):
            # Randomly choose if a score will be attempted to be increased by 2
            add_two = bool(random.getrandbits(1))
            # Get the index for score 1
            index_one = _get_score_below_20(ability_scores)
            # Score can be increased by 2 if its under 19
            if add_two and ability_scores[index_one] < 19:
                ability_scores[index_one] += 2
            # Otherwise just increase two scores by 1
            else:
                index_two = _get_score_below_20(ability_scores, second_index=index_one)
                ability_scores[index_one] += 1
                ability_scores[index_two] += 1
            # Decrease the level by 1 until the next factor of 4 (16) Used for levels 19+
            if level > 16:
                level -= 1
            # Otherwise you decrease it to the next factor of 4
            else:
                level -= 4
        # While the level is still above 0 decrement
        elif level > 0:
            level -= 1
        else:
            break

    return ability_scores

# Function used to roll a character's hit points given their level, their die size,
# and their constitution score. Negative constitution scores are ignored.
def random_hit_points(die_size: int, level: int, constitution_score: int) -> int:
    con_mod = math_utils.get_ability_mod(constitution_score)

    # If the constitution modifier is lower than 0 then ignore it
    if con_mod < 0:
        con_mod = 0

    # For first level add full die_size to hit_points
    hit_points = die_size + con_mod

    # Roll for every other level
    for i in range(level - 1):
        hit_points += random.randint(1, die_size) + con_mod

    return hit_points

# Function used to return a random alignment
def random_alignment() -> Alignment:
    return random.choice(list(Alignment))

# Function used to return a random age given a maximum racial age
def random_age(max_age: int) -> int:
    return random.randint(1, max_age)

# Function used to return a random gender
def random_gender() -> Gender:
    return random.choice(list(Gender))

# Function used to get a random value from a file given a column index
# and the file path itself. A space is returned if the file could
# not be found.
def random_value_from_file(file_path: str, elementOrIndex, is_sorted=False) -> str:
    list_of_traits = io.get_col(elementOrIndex, file_path, is_sorted)
    if list_of_traits is not None:
        # Convert to list and pop off the header element of the list
        list_of_traits = list(list_of_traits)
        list_of_traits.pop(0)
        return random.choice(list_of_traits)
    else:
        return " "

# Function used to get a random full name given a file path
# and the gender of that character (currently just Male and Female)
def random_name (file_path: str, gender: Gender) -> str:
    name = ""
    # Get the first name for either a male or female character
    if gender == Gender.Male:
        name += random_value_from_file(file_path, 1)
    else:
        name += random_value_from_file(file_path, 2)
    # Finally add a last name and return the value
    name += " " + random_value_from_file(file_path, 3)
    return name

# Function that returns a random sub list given a list and a number
# of elements to include. The list returned does not have repeating
# elements.
def random_list (list: [], num_of_items: int) -> []:

    # If number of items is greater than or equal
    # to the list length, just return the list.
    if num_of_items >= len(list):
        return list

    final_list = []
    # Loop list until a unique sublist is created
    while num_of_items > 0:
        item = random.choice(list)
        if item not in final_list:
            final_list.append(item)
            num_of_items -= 1

    return final_list

# Function used to select random equipment,languages or proficiencies given a list of strings
# representing choices of state category that can be made.
# Certain flags are used to indicate attributes about these choices such as
# "!" representing multiple unique items that can be added to the final list
# if this choice is selected. (/,?,!,*,@)
def random_equip_or_lang_or_pro (list: [], file_path: str, is_armor: bool) -> []:
    final_list = []

    # Loop through various item selections in the list, make a choice,
    # and then add the selected item to the final list.
    for item in list:
        # Get the selection of items by splitting the given string
        line = item.split("/")
        invalid_choice = True
        # Continue until a proper item is chosen for the list
        while invalid_choice:
            # Begin with a random item from the selection
            element = str(random.choice(line))
            # If it starts with a "?" then this is a category of item and an item
            # of that category is chosen at random given the file path with that list
            if file_path != None and element.startswith("?"):
                element = random_value_from_file(file_path, element[1:])
            # Confirm that item is not already in list and does not have
            # a needed requirement
            if element not in final_list and not element.startswith("*"):
                # If it starts with "!" this means multiple unique items are a part of
                # this choice and all must be individually added.
                if "!" in element:
                    element_list = element.split("!")
                    for sub_element in element_list:
                        final_list.append(sub_element)
                else:
                    final_list.append(element)
            invalid_choice = False

    # A final run through of the list must be preformed searching for
    # an "@" character in the selected items (if there is one).
    remove_item = []
    add_item = []

    for item in final_list:
        # If it starts with an "@" then this means multiple of the same item
        # should be added to the final list
        if "@" in item:
            multi_items = item.split("@")
            # Add original string so it can be removed from the final list
            remove_item.append(item)
            # Add the needed copies to the add item list
            for i in range(int(multi_items[0])):
                add_item.append(multi_items[1])

    # Add/Remove elements in final list if needed
    for item in remove_item:
        final_list.remove(item)
    for item in add_item:
        final_list.append(item)

    return final_list

# Function that returns a random race given a level
def random_race (level: int) -> Race:
    # Get the contents of all the available races
    race_list = io.get_row(1, io.RACE_FILE_PATH)
    # Create a random race with an index from the range of 1 to
    # length of list
    return Race(random.randint(1, len(race_list)), level)

# Function that returns a random background given an alignment
def random_background (alignment: Alignment) -> Background:
    # New background is generated from list of all available backgrounds
    bkgr_list = io.get_row(1, io.BKGR_ATRBT_FILE_PATH)
    background = Background(alignment, random.randint(1, len(bkgr_list)))
    # Ideal is set using helper function
    _random_ideal(background)

    # Background index is obtained so personality traits, bonds, and flaws can be set.
    bkgr_index = background.get_index()
    background.personality_trait = random_value_from_file(io.BKGR_PERS_TRT_FILE_PATH, bkgr_index)
    background.bond = random_value_from_file(io.BKGR_BONDS_FILE_PATH, bkgr_index)
    background.flaw = random_value_from_file(io.BKGR_FLAWS_FILE_PATH, bkgr_index)

    # Loop through tool proficiencies in case a specific tool needs to be chosen.
    tool_prof = background.tool_prof
    equip = background.equipment
    for i in range(len(tool_prof)):
        if tool_prof[i].startswith("*"):
            # Randomly choose a tool depending on the category specified.
            new_tool_prof = random_value_from_file(io.TOOL_TYPE_FILE_PATH,
                                                   tool_prof[i][1:])
            # Replace corresponding equipment with tool selected.
            for j in range(len(equip)):
                if equip[j].lower() == tool_prof[i].lower():
                    equip[j] = new_tool_prof
                    break
            tool_prof[i] = new_tool_prof

    return background

# Helper Function used to set a background's ideal randomly.
def _random_ideal (background: Background):
    # Get background's list of ideals
    ideals_list = background.get_ideals_list()
    # Continue until a match is made between the background's alignment
    # and the chosen ideal
    while True:
        ideal_index = random.randint(1, len(ideals_list) - 1)
        if background.set_ideal(ideal_index):
            break

# Function used to create a random dnd class given a level, ability scores,
# and a race and a background (these last two parameters are optional)
# This function makes a completely random dnd class regardless of the
# ability scores.
def random_dnd_class(level: int, ability_scores: [], race: Race,
                     background: Background) -> DndClass:
    # Get total list of classes available to the current program and make a random
    # class choice
    class_list = io.get_row(1, io.CLASS_STAND_FILE_PATH)
    class_name = random.choice(class_list)
    dndclass = DndClass(class_name, level, ability_scores, race, background)

    # If the class was successfully made then continue
    if dndclass is not None:
        # Get attributes of class that need further choices to be made
        choice_list = dndclass.get_choice_attributes_list()
        line = choice_list[1].split("=")
        # Choose what skills the class will add its proficiency bonus to.
        sub_line = line[1].split("/")
        if dndclass.set_skill_bonus(random_list(sub_line, int(line[0]))) == False:
            return None

        # Set the classes weapons, armor and items depending on its
        # proficiencies.
        dndclass.weapons = (random_equip_or_lang_or_pro(
            choice_list[2].split("="), io.WEAPON_TYPE_FILE_PATH, False))
        dndclass.armor = (random_equip_or_lang_or_pro(
            choice_list[3].split("="), io.ARMOR_TYPE_FILE_PATH, True))
        dndclass.items = (random_equip_or_lang_or_pro(
            choice_list[4].split("="), None, False))

        # Figure out if class has access to its archetypes at this level.
        archetype_list = choice_list[5].split("=")
        arche_level = int(archetype_list[0])

        # Select a given archetype if the class has access to it at the level
        if arche_level != 0 and level >= arche_level:
            line = io.get_row(1, archetype_list[2])
            index = random.randint(1, len(line))

            # Set the traits of this archetype and if it is a spell caster,
            # see if any additional spells need to be finalized.
            dndclass.set_archetype_name(archetype_list[1] +
                                        " " + line[index - 1])

            need_to_set_spells = \
                dndclass.set_archetype_attributes(archetype_list[2], index)
            if need_to_set_spells:
                dndclass.spells = _finalize_spells(dndclass.spells)

        # If the class has access to spells then fill up its spell list randomly.
        if dndclass.spells is not None:
            dndclass.spells = random_spells(dndclass.spells, dndclass.get_spell_slots(),
                                            dndclass.get_spell_list_file_path(), dndclass.get_level(),
                                            dndclass.ability_scores[
                                                math_utils.get_casting_ability_pos(
                                                    dndclass.get_casting_ability())],
                                            dndclass.get_spells_known())

        # Add additional level information to its attacks and spell casting
        # abilities.
        dndclass.set_attacks_and_spell_casting(dnd_mod.finalize_attacks_and_spell_casting(
            list(dndclass.get_attacks_and_spell_casting()), dndclass.get_level()))

        # Finally, if further choices need to be made regarding proficiencies/skill bonuses then do so.
        dndclass.set_weapon_prof(tuple(random_equip_or_lang_or_pro(list(dndclass.get_weapon_prof()),
                                                                   io.WEAPON_TYPE_FILE_PATH, False)))
        dndclass.set_armor_prof((tuple(random_equip_or_lang_or_pro(list(dndclass.get_armor_prof()),
                                                                   io.ARMOR_TYPE_FILE_PATH, True))))
        dndclass.set_tool_prof((tuple(random_equip_or_lang_or_pro(list(dndclass.get_tool_prof()),
                                                                  io.TOOL_TYPE_FILE_PATH, False))))
        dndclass.set_skill_bonuses((tuple(random_equip_or_lang_or_pro(list(dndclass.get_skill_bonuses()),
                                                                      None, False))))

    return dndclass

def random_character_sheet(dndClass: DndClass, gender: Gender, name: str, age: int) -> CharacterSheet:
    characterSheet = CharacterSheet(dndClass, gender, name, age)
    characterSheet.set_hit_points(random_hit_points(dndClass.get_hit_die(),
                                               dndClass.get_level(),
                                               characterSheet.get_ability_modifiers()[2]))
    characterSheet.set_languages(random_equip_or_lang_or_pro(list(characterSheet.get_languages()),
                            io.LANGUAGE_FILE_PATH, False))

    return characterSheet

def completely_random_character_sheet() -> CharacterSheet:
    alignment = random_alignment()
    bkgr = random_background(alignment)
    level = random_level()
    race = random_race(level)
    gender = random_gender()
    name = random_name(race.get_racial_name_file_path(), gender)
    age = random_age(race.get_max_age())
    ability_scores = random_ability_scores()
    dndClass = random_dnd_class(level, ability_scores, race, bkgr)
    characterSheet = random_character_sheet(dndClass, gender, name, age)

    return characterSheet

# Function which returns a random spell list given an empty or partially filled spell list,
# list representing a caster's spell slots, the file path to the spell list,
# level of the caster, score of the casting ability and spells known if they are
# a known caster.
# Spell list returned will not have any duplicate spells in its list.
def random_spells(spells: [], spell_slots: (), spell_list_file_path: str,
                  level: int, casting_ability_score: int, spells_known: int) -> []:
    # Get number of spells that need to be set for the spell list.
    # If it is a prepared caster then casting mod + level is the total spells they
    # can prepare.
    if spells_known == -1:
        modifier = math_utils.get_ability_mod(casting_ability_score) if casting_ability_score > 9 \
            else 0
        number_of_spells = level + modifier
    # Known spell casters just use a set number for spells known.
    else:
        number_of_spells = spells_known

    # Get the spell list needed up to the maximum level spell that can be cast.
    max_spell_level = len(spell_slots)
    spell_list = [[] for i in range(len(spell_slots))]
    for i in range(max_spell_level):
        spell_list[i] = list(io.get_col(i +1, spell_list_file_path, False))
        spell_list[i].pop(0)

    # Set cantrips of list based on the available amount of space allotted by
    # the spells slots.
    for i in range(spell_slots[0]):
        while True:
            spell = random.choice(spell_list[0])
            if spell not in spells[0]:
                spells[0].append(spell)
                break

    # For the number of spells that can be chosen, select a random spell level,
    # (1 - maximum spell level) and attempt to add that to the total spell list
    for i in range(number_of_spells):
        while True:
            random_spell_level = random.randint(1, max_spell_level - 1)
            spell = random.choice(spell_list[random_spell_level])
            # Do not add duplicate spells to the spell list
            if spell not in spells[random_spell_level]:
                spells[random_spell_level].append(spell)
                break

    return spells

# Function used to finish selecting spells if class requires further choice
# from the player.
def _finalize_spells(spells: []) -> []:
    # Used to keep track of current spell level.
    counter = 0
    # Go through each spell level in the class's list
    for spell_level in spells:
        # Go through each individual spell
        for spell in spell_level:
            # Extract the file path to the spell list that a selection needs to be made from.
            if spell.startswith("*"):
                file_path = spell[1:]
                line = list(io.get_col(1 + counter, file_path, False))
                line.pop(0)
                # Get index of current spell so that it may be altered
                index = spell_level.index(spell)
                # Only add spells to the class that the class does not already know.
                while True:
                    new_spell = random.choice(line)
                    if new_spell not in spell_level:
                        spell_level[index] = new_spell
                        break
        counter += 1
    return spells

# Helper Function used to get random index of ability score that is not
# 20 (can not be increased). If two scores need to be increased then
# a second index maybe passed in as well to avoid increasing the
# same score twice.
def _get_score_below_20 (ability_scores: [], second_index = -1) -> int:
    while True:
        index = random.randint(0, 5)
        if ability_scores[index] < 20 and index != second_index:
            return index