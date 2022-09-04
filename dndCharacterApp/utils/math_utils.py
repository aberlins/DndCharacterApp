# ----------------------------------------------------------------------------------------------- #
# Module which contains methods math related functions to use throughout the program.
# ----------------------------------------------------------------------------------------------- #

import math
import dndCharacterApp.utils.io_utils as io
from dndCharacterApp.utils.gen_utils import SKILL_NAMES

# Function gets ability score modifier given a single score
def get_ability_mod (ability_score: int) -> int:
    # Calculate as normal when greater than 9, round down else wise
    if ability_score > 9:
        return int((ability_score - 10) / 2)
    else:
        score = (ability_score - 10)
    return int(math.floor(score / 2))

# Function which returns saving throws, given: a list of ability scores,
# a tuple of the class's saving throws, and the class's proficiency bonus
# If any of the ability scores/saving throws are not formatted correctly None is returned.
def get_saving_throw_scores(ability_scores: [], saving_throws: (), prof_bonus: int) -> []:
    final_saves = []
    # list filled with 0s so indexes can be referenced later
    prof_bonus_list = [0 for i in range(6)]

    # If the list of ability scores passed in contain all ints, calculate
    # there corresponding ability score mods
    for i in range(6):
        if isinstance(ability_scores[i], int):
            final_saves.append(get_ability_mod(ability_scores[i]))
        else:
            return None

    # Search through the tuple of saving throws and match the index
    # to the corresponding ability
    for abil in saving_throws:
        match(abil.lower()):
            case "strength":
                index = 0
            case "dexterity":
                index = 1
            case "constitution":
                index = 2
            case "intelligence":
                index = 3
            case "wisdom":
                index = 4
            case "charisma":
                index = 5
            case _:
                index = -1

        # Confirm that saving throws had proper names for the abilities
        if index != -1:
            prof_bonus_list[index] = prof_bonus
        else:
            return None

    # Return the final scores by adding the ability score mods and prof bonuses.
    for i in range(6):
        final_saves[i] += prof_bonus_list[i]

    return final_saves

# Function which returns skill scores, given: a list of ability scores,
# a list of the character's skill bonuses, and the class's proficiency bonus
# If any of the ability scores/skill bonuses are not formatted correctly None is returned.
def get_skill_scores(ability_scores: [], skill_bonuses: [], prof_bonus: int, extra_bonuses: {}) -> []:

    # list filled with 0s/Falses so indexes can be referenced later
    add_prof_bonus = [False for i in range(len(SKILL_NAMES))]
    skill_scores = [0 for i in range(len(SKILL_NAMES))]

    # Set corresponding boolean values to true if the skill bonuses match
    for bonus in skill_bonuses:
        index = 0
        while True:
            # Check to see if index has reached past skill name's length
            if index >= len(SKILL_NAMES):
                return None
            if SKILL_NAMES[index].lower() == bonus.lower():
                add_prof_bonus[index] = True
                break
            index += 1

    # Depending on the skill specified, set the index to that corresponding ability score
    # (i.e. Strength ability mod should be used when calculating Athletics score.)
    for i in range(len(SKILL_NAMES)):
        match (SKILL_NAMES[i].lower()):
            case "athletics":
                index = 0
            case "acrobatics" | "sleight of hand" | "stealth":
                index = 1
            case "arcana" | "history" | "investigation" | "nature" | "religion":
                index = 3
            case "animal handling" | "insight" | "medicine" | "perception" | "survival":
                index = 4
            case "deception" | "intimidation" | "performance" | "persuasion":
                index = 5
            # Return none if skill score list is improperly formatted.
            case _:
                return None

        # Check if ability score is an int before calculating the save.
        if isinstance(ability_scores[index],int):
            skill_scores[i] = get_skill_score(ability_scores[index], add_prof_bonus[i], prof_bonus)
        else:
            return None

    # Add extra bonuses to the skills if the class or anything else grants it.
    if extra_bonuses is not None:
        # First match the bonus with the corresponding skill to get the proper index.
        for bonus in extra_bonuses.keys():
            for skill in SKILL_NAMES:
                if bonus.lower() == skill.lower():
                    index = SKILL_NAMES.index(skill)
                    break
            # Get the total bonuses that are assigned to the character
            total_bonuses = extra_bonuses[bonus].split("=")
            # Subtract the original proficiency bonus if it was already added.
            if add_prof_bonus[index]:
                skill_scores[index] = skill_scores[index] - prof_bonus
            # For every bonus, add it to the final total.
            for entry in total_bonuses:
                sub_entry = entry.split("/")
                # If there is an x in the beginning multiply the proficiency bonus and then add it
                # to the skill score.
                if sub_entry[0] == "x":
                    skill_scores[index] = skill_scores[index] + (prof_bonus * int(sub_entry[1]))
                # Otherwise, add it to the skill
                else:
                    # Re-add the proficiency bonus if it was removed.
                    if add_prof_bonus[index]:
                        skill_scores[index] = skill_scores[index] + (prof_bonus + int(sub_entry[1]))
                    else:
                        skill_scores[index] = skill_scores[index] + int(sub_entry[1])

    return skill_scores

# Function which calculates a skill score given an ability score, the proficiency bonus
# and a boolean which specifies if the proficiency bonus should be applied.
def get_skill_score(ability_score: int, add_prof_bonus: bool, prof_bonus: int) -> int:
    return get_ability_mod(ability_score) + prof_bonus if add_prof_bonus \
        else get_ability_mod(ability_score)

# Function which calculates a character's initiative score give their dexterity score,
# and any bonuses that can be applied. -1 is returned for any improper formatting errors.
def get_initiative_score(dexterity_score: int, bonuses: []) -> int:
    init = get_ability_mod(dexterity_score)

    # If bonuses is not None and contains ints then add them to the current score
    if bonuses is not None:
        for bonus in bonuses:
            if isinstance(bonus, int):
                init += bonus
            else:
                return -1

    return init

# Function which calculates a character's speed given their racial speed,
# and any bonuses that can be applied. -1 is returned for any improper formatting errors.
def get_speed(speed: int, bonuses: []) -> int:

    # If bonuses is not None and contains ints then add them to the current score
    if bonuses is not None:
        for bonus in bonuses:
            if isinstance(bonus, int):
                speed += bonus
            else:
                return -1
    return speed

# Function which calculates a character's passive wisdom score give their perception score,
# and any bonuses that can be applied.
def get_passive_wisdom_score(perception: int, bonus: int) -> int:
    return perception + bonus + 10

# Function which calculates a character's armor class given their dexterity score and list
# of armors. -1 is returned if there is any formatting errors.
def get_armor_class(dexterity_score: int, armors: []) -> int:
    dex_bonus = get_ability_mod(dexterity_score)
    armor_class = 0

    # If the character doesn't wear any armor then their ac = 10 + dexterity mod
    if armors is None or len(armors) == 0:
        return dex_bonus + 10

    # Apply bonuses to ac for every piece of armor
    for armor in armors:
        # Get the armor's stats
        armor_stats = io.get_col(armor, io.ARMOR_STATS_FILE_PATH, True)
        # Continue if successful return -1 if not
        if armor_stats is not None:
            add_dex = armor_stats[2].split("=")
        else:
            return -1

        # If you can add your dexterity mod continue here
        if add_dex[0].lower() == "true":
            # If there is a limit to the amount of your mod you can add continue here
            if add_dex[1].lower() == "true":
                # If the dex bonus is greater then the limit, add the stats and limit to ac
                if int(add_dex[2]) < dex_bonus:
                    armor_class += armor_stats[1] + int(add_dex[2])
                # Otherwise add your dex mod and stats to ac
                else:
                    armor_class += armor_stats[1] + dex_bonus
            # Otherwise add your dex mod and stats to ac
            else:
                armor_class += armor_stats[1] + dex_bonus
        # Otherwise just add the stats of the armor to the ac
        else:
            armor_class += armor_stats[1]

    # If the character is only carrying a shield then add the dex bonus and 10 to the ac
    if len(armors) == 1 and armors[0] == "Shield":
        armor_class += dex_bonus + 10

    return armor_class

# Function which calculates a character's attack bonus given their dexterity score, strength score
# proficiency bonus and a weapon. -1 is returned if there is any formatting errors.
def get_attack_bonus(strength_score: int, dexterity_score: int, prof_bonus: int,
                     weapon: str) -> int:

    weapon_stats = io.get_col(weapon, io.WEAPONS_STATS_FILE_PATH, True)

    if weapon_stats is not None:
        ability_mod = 0
        # If the weapon is ranged then use the dex score to calculate ab
        if weapon_stats[2].split("=")[0].lower() == "true":
            ability_mod = get_ability_mod(dexterity_score)
        # If the weapon has the finesse use either dex or str score which ever is higher
        elif weapon_stats[3].split("=")[0].lower() == "true":
            if (dexterity_score > strength_score):
                ability_mod = get_ability_mod(dexterity_score)
            else:
                ability_mod = get_ability_mod(strength_score)
        # For all other weapons use strength score
        else:
            ability_mod = get_ability_mod(strength_score)
    # Return -1 if weapon is not in file.
    else:
        return -1

    return ability_mod + prof_bonus

# Function which calculates a character's spell attack bonus given their casting ability,
# ability scores and their proficiency bonus. -1 is returned if there is any formatting errors.
def get_spell_attack_bonus(ability_scores: [], casting_ability: str, prof_bonus:int) -> int:

    index = 0

    # Get the index of the casting ability
    index = get_casting_ability_pos(casting_ability)
    if index == -1:
        return index

    return prof_bonus + get_ability_mod(ability_scores[index])

# Function which calculates a character's spell save dc given their casting ability,
# ability scores and their proficiency bonus. -1 is returned if there is any formatting errors.
def get_spell_save_dc(ability_scores: [], casting_ability: str, prof_bonus:int) -> int:
    return get_spell_attack_bonus(ability_scores, casting_ability, prof_bonus) + 8

def get_casting_ability_pos(casting_ability: str) -> int:
    match (casting_ability.lower()):
        case "intelligence":
            return 3
        case "wisdom":
            return 4
        case "charisma":
            return 5
        case _:
            return -1