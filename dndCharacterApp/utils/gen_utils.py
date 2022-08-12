# ----------------------------------------------------------------------------------------------- #
# Module which contains tuples/methods that are used throughout
# various points in the program.
# ----------------------------------------------------------------------------------------------- #
SKILL_NAMES = ("Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History",
			"Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception",
            "Performance", "Persuasion", "Religion", "Sleight Of Hand", "Stealth", "Survival")
ABILITY_NAMES = ("Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma")

def list_with_commas(list: ()) -> str:
    final_list = ""
    if list is not None:
        for item in list:
            final_list += str(item) + ", "

    if len(final_list) > 0:
        return final_list[:-2]
    else:
        return final_list

