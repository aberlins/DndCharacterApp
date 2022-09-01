
from dndCharacterApp.dndEntities.dnd_enums import Gender as Gender
from dndCharacterApp.dndEntities.dndRace import Race as Race
from dndCharacterApp.dndEntities.dndBackground import Background as Background
from dndCharacterApp.dndEntities.dnd_class import DndClass as DndClass
from dndCharacterApp.dndEntities.dnd_enums import Alignment as Alignment
import dndCharacterApp.utils.math_utils as math
import dndCharacterApp.utils.io_utils as io
import dndCharacterApp.utils.gen_utils as gen


class CharacterSheet:

    def __init__(self, dndClass: DndClass, gender: Gender, name: str, age: int,
                 race=None, background=None):
        self._name = name
        self._gender = gender
        self._age = age
        self._dndClass = dndClass
        self._hit_points = -1

        # Set the character sheet's race as the dnd class if the dnd class has one
        # if not attempt to assign a given race to both the character sheet and class
        # Assign None if both conditions are not met.
        if self._dndClass is not None:
            self._level = self._dndClass.get_level()
            if self._dndClass.get_race() is not None:
                self._race = self._dndClass.get_race()
            elif race is not None:
                if self._dndClass.set_race(race):
                    self._race = race
            else:
                self._race = None
            # Set the character sheet's background as the dnd class if the dnd class has one
            # if not attempt to assign a given background to both the character sheet and class
            # Assign None if both conditions are not met.
            if self._dndClass.get_background() is not None:
                self._background = self._dndClass.get_background()
            elif background is not None:
                self._dndClass.set_background(background)
                self._background = background
            else:
                self._background = None
        else:
            self._level = -1

        # If the class, race and background are present then set the final lists for the sheet.
        if self._dndClass is not None and self._race is not None and self._background is not None:
            self._set_final_lists()
        else:
            self._set_none_attributes()


    def _set_final_lists(self):
        self._languages = _combine_lists(self._race.get_languages(),
                                         self._background.languages,
                                         three_list=self._dndClass.languages)
        self._armor_prof = _combine_lists(self._race.get_armor_prof(),
                                          self._dndClass.get_armor_prof())
        self._weapon_prof = _combine_lists(self._race.get_weapon_prof(),
                                           self._dndClass.get_weapon_prof())
        self._tool_prof = _combine_lists(self._race.get_tool_prof(), self._background.tool_prof,
                                         three_list=self._dndClass.get_tool_prof())
        self._skill_prof = _combine_lists(self._background.get_skill_prof(),
                                          self._dndClass.get_skill_bonuses())
        self._equipment = _combine_lists(self._background.equipment, self._dndClass.items,
                                         duplicates=True)

    def _set_none_attributes(self):
        self._languages = None
        self._armor_prof = None
        self._weapon_prof = None
        self._tool_prof = None
        self._skill_prof = None
        self._equipment = None

    def set_hit_points(self, hit_points: int):
        self._hit_points = hit_points

    def set_languages(self, languages: str):
        self._languages = languages

    # List of getters for all attributes of the character sheet class.
    def get_all_proficiencies(self):
        return _combine_lists(self._tool_prof, self._weapon_prof, three_list=self._armor_prof,
                              duplicates=True)

    def get_name(self) -> str:
        return self._name

    def get_gender(self) -> Gender:
        return self._gender

    def get_age(self) -> int:
        return self._age

    def get_alignment(self) -> Alignment:
        if self._background is not None:
            return self._background.get_alignment()
        else:
            return None

    def get_personality_trait(self) -> str:
        if self._background is not None:
            return self._background.personality_trait
        else:
            return ""

    def get_ideal(self) -> str:
        if self._background is not None:
            return self._background.get_ideal()
        else:
            return ""

    def get_bond(self) -> str:
        if self._background is not None:
            return self._background.bond
        else:
            return ""

    def get_flaw(self) -> str:
        if self._background is not None:
            return self._background.flaw
        else:
            return ""

    def get_money(self) -> ():
        if self._background is not None:
            return tuple(self._background.get_money())
        else:
            return None

    def get_ability_scores(self) -> ():
        if self._dndClass is not None:
            return tuple(self._dndClass.ability_scores)
        else:
            return None

    def get_ability_modifiers(self) -> ():
        mod = []
        if self._dndClass is not None:
            for score in self._dndClass.ability_scores:
                mod.append(math.get_ability_mod(score))
        return tuple(mod)

    def get_saving_throw_scores(self) -> ():
        if self._dndClass is not None:
            return tuple(math.get_saving_throw_scores(self.get_ability_scores(),
                                                      self._dndClass.get_saving_throws(),
                                                      self.get_prof_bonus()))
        return None

    def get_saving_throw_prof(self) -> ():
        if self._dndClass is not None:
            return tuple(self._dndClass.get_saving_throws())
        return None

    def get_skill_scores(self) -> ():
        if self._dndClass is not None:
            return tuple(math.get_skill_scores(self.get_ability_scores(), self._skill_prof,
                                         self.get_prof_bonus()))
        else:
            return None

    def get_skill_prof(self) -> ():
        return self._skill_prof

    def get_languages(self) -> ():
        return self._languages

    def get_hit_points(self) -> int:
        return self._hit_points

    def get_hit_die(self) -> str:
        if self._dndClass is not None:
            return str(self.get_level()) + "d" + str(self._dndClass.get_hit_die())
        return ""

    def get_level(self) -> int:
        return self._level

    def get_initiative(self) -> int:
        if self._dndClass is not None:
            bonus_int = self._dndClass.get_init_bonus()
            return math.get_initiative_score(self.get_ability_scores()[1], bonus_int)
        return -1

    def get_prof_bonus(self) -> int:
        if self._dndClass is not None:
            return self._dndClass.get_prof_bonus()
        return -1

    def get_speed(self) -> int:
        if self._race is not None and self._dndClass is not None:
            return math.get_speed(self._race.get_speed(), self._dndClass.get_speed_bonus())
        return -1

    def get_armor_class(self) -> int:
        if self._dndClass is not None:
            armors = self._dndClass.armor
            if armors is not None:
                return math.get_armor_class(self.get_ability_scores()[1], armors)
            # Special ac is used for classes like the monk who get bonuses while wearing no
            # armor.
            elif self._dndClass.get_special_ac() is not None:
                return self._dndClass.get_special_ac()
        return -1

    # Update needed for possible bonuses
    def get_passive_wisdom(self) -> int:
        if self._dndClass is not None:
            return math.get_passive_wisdom_score(self.get_skill_scores()[11],0)
        return -1

    def get_casting_ability(self) -> str:
        if self._dndClass is not None:
            return self._dndClass.get_casting_ability()
        return None

    def get_prepared_or_known(self) -> str:
        if self._dndClass is not None:
            return self._dndClass.get_prepared_or_known()
        return ""

    def get_spell_attack_bonus(self) -> int:
        if self._dndClass is not None:
            return self._dndClass.get_spell_attack_bonus()
        return -1

    def get_spell_save_dc(self) -> int:
        if self._dndClass is not None:
            return self._dndClass.get_spell_save_dc()
        return -1

    def get_armors(self) -> ():
        if self._dndClass is not None:
            return tuple(self._dndClass.armor)
        return None

    def get_weapons(self) -> ():
        if self._dndClass is not None:
            return tuple(self._dndClass.weapons)
        return None

    def get_weapon_stats(self) -> ():
        if self._dndClass is not None:
            # Go through all weapons class has and gather all data needed on it
            weapon_stats = []
            for weapon in self.get_weapons():
                # Get information from file
                weapon_info = io.get_col(weapon, io.WEAPONS_STATS_FILE_PATH, True)
                damage_info = weapon_info[1].split("=")

                # For each entry get the weapon's name, its attack bonus and its damage
                weapon_entry = []
                weapon_entry.append(weapon)
                scores = self.get_ability_scores()
                att_bonus = math.get_attack_bonus(scores[0], scores[1], self.get_prof_bonus(), weapon)
                weapon_entry.append(str(att_bonus))
                weapon_entry.append(damage_info[0] + "/" + damage_info[1])

                # Append the entry to the total weapons list
                weapon_stats.append(weapon_entry)
            return weapon_stats
        return None

    def get_equipment(self) -> ():
        return tuple(self._equipment)

    def get_attacks_and_spell_casting(self) -> ():
        if self._dndClass is not None:
            return self._dndClass.get_attacks_and_spell_casting()
        return None

    def get_class_spells(self) -> ():
        if self._dndClass is not None and self.get_casting_ability() is not None:
            return tuple(self._dndClass.spells)
        return None

    def get_race_spells(self) -> ():
        if self._race is not None and self._race.get_casting_ability() is not None:
            return tuple(self._race.get_spells())
        return None

    def get_class_spell_slots(self) -> ():
        if self._dndClass is not None and self.get_casting_ability() is not None:
            return tuple(self._dndClass.get_spell_slots())
        return None

    def get_background_name(self) -> str:
        if self._background is not None:
            return self._background.name
        return ""

    def get_race_name(self) -> str:
        if self._race is not None:
            return self._race.get_name()
        return ""

    def get_class_name(self) -> str:
        if self._dndClass is not None:
            return self._dndClass.get_name()
        return ""

    def get_archetype_name(self) -> str:
        if self._dndClass is not None:
            return self._dndClass.get_archetype_name()
        return ""

    def get_archetype_short_name(self) -> str:
        if self.get_archetype_name() != "":
            index = self.get_archetype_name().index(":") + 2
            return self.get_archetype_name()[index:]
        return ""

    def get_race_features(self) -> ():
        if self._race is not None:
            return tuple(self._race.get_features())
        return None

    def get_bkgr_features(self) -> ():
        if self._background is not None:
            return self._background.get_features()
        return None

    def get_class_features(self) -> ():
        if self._dndClass is not None:
            return self._dndClass.get_features()
        return None

    def get_skill_prof_list(self) -> ():
        if self._skill_prof is not None:
            return _set_bool_prof_list(gen.SKILL_NAMES, self._skill_prof)
        return None

    def get_save_prof_list(self) -> ():
        if self._dndClass is not None:
            return _set_bool_prof_list(gen.ABILITY_NAMES, self.get_saving_throw_prof())

    # Functions that return a string representation of lists of items or features to the sheet
    def proficiency_str(self) -> str:
        prof_str = "Proficiencies: "
        return prof_str + gen.list_with_commas(self.get_all_proficiencies())

    def equipment_str(self) -> str:
        equip_str = gen.list_with_commas(self.get_equipment()) + ", "

        # Add only first 3 weapons that the sheet has.
        weapons = self.get_weapons()
        max_weapons = 3
        for weapon in weapons:
            if max_weapons > 0:
                equip_str += weapon + ", "
            else:
                break
            max_weapons -= 1

        return equip_str + gen.list_with_commas(self.get_armors())

    def language_str(self) -> str:
        lang_str = "Languages: "
        return lang_str + gen.list_with_commas(self._languages)

    def feature_str(self) -> str:
        feat_str = ""
        if self.get_archetype_name() is not None:
            feat_str += self.get_archetype_name() + "\n"
        feat_str += "Gender: " + str(self.get_gender()) + "\tAge: " + str(self.get_age()) + "\n\n"
        feat_str += "Background Features: "
        feat_str += gen.list_with_commas(self.get_bkgr_features()) + "\n\n"
        feat_str += "Racial Features: "
        feat_str += gen.list_with_commas(self.get_race_features()) + "\n"
        if self.get_race_spells() is not None:
            feat_str += "Racial Spells: "
            for spell in self.get_race_spells():
                feat_str += spell + ", "
            feat_str = feat_str[:-2]
        feat_str += "\n\nClass Features: "
        return feat_str + gen.list_with_commas(self.get_class_features())

    def attack_and_spell_casting_str(self) -> str:
        att_str = ""
        if self.get_attacks_and_spell_casting() is not None:
            for spell_att in self.get_attacks_and_spell_casting():
                att_str += spell_att + "\n"

        if len(att_str) > 0:
            return att_str[:-1]
        else:
            return att_str

    # Functions used to return an ordered tuple that is meant to fill the various fields
    # within the program's pdf file
    def string_field_pdf_data(self) -> ():
        data = []
        # Basic information of the sheet
        data.append(str(self.get_level()) + " " + self.get_class_name())
        data.append(self.get_background_name())
        data.append(self.get_name())
        data.append(self.get_race_name())
        data.append(str(self.get_alignment()))
        data.append(str(self.get_prof_bonus()))
        data.append(str(self.get_armor_class()))
        data.append(str(self.get_initiative()))
        data.append(str(self.get_speed()))
        data.append(str(self.get_hit_points()))
        data.append(str(self.get_hit_points()))
        data.append(self.get_hit_die())
        data.append(self.get_hit_die())
        data.append(str(self.get_passive_wisdom()))
        data.append(self.get_personality_trait())
        data.append(self.get_ideal())
        data.append(self.get_bond())
        data.append(self.get_flaw())
        data.append(self.proficiency_str() + "\n\n" + self.language_str())
        data.append(self.equipment_str())

        # Associated stats of the sheet, like ability scores and skill scores
        for stat in self.get_ability_scores():
            data.append(str(stat))
        for mod in self.get_ability_modifiers():
            data.append(str(mod))
        for save in self.get_saving_throw_scores():
            data.append(str(save))
        for skill in self.get_skill_scores():
            data.append(str(skill))

        # Weapons and their stats for the sheet, maximum of 3 allowed
        weapons = self.get_weapon_stats()
        for i in range(len(weapons)):
            if i == 3:
                break
            for info in weapons[i]:
                data.append(info)
        if len(weapons) < 3:
            if len(weapons) == 1:
                ran = 6
            else:
                ran = 3
            for i in range(ran):
                data.append("")

        # Money for character sheet
        for mon in self.get_money():
            data.append(mon)

        # Features/Spells and attacks of the sheet
        data.append(self.feature_str())
        data.append(self.attack_and_spell_casting_str())

        # Finally add information associated with casting if the character is a caster,
        # Add empty strings if otherwise.
        if self.get_casting_ability() is not None:
            data.append(self.get_archetype_short_name() + " " + self.get_class_name())
            data.append(self.get_casting_ability())
            data.append(str(self.get_spell_save_dc()))
            data.append(str(self.get_spell_attack_bonus()))
        else:
            for i in range(4):
                data.append("")

        return tuple(data)

    def button_pdf_data(self) -> ():
        button_data = []

        # Get boolean representation of saves and skills
        saves = self.get_save_prof_list()
        skills = self.get_skill_prof_list()

        # Add the contents to the button list, if the list returned is none
        # fill the values with false instead.
        if saves is not None:
            for save in saves:
                button_data.append(save)
        else:
            for i in range(len(gen.ABILITY_NAMES)):
                button_data.append(False)

        if skills is not None:
            for skill in skills:
                button_data.append(skill)
        else:
            for i in range(len(gen.SKILL_NAMES)):
                button_data.append(False)

        return tuple(button_data)

    # Function used to create a pdf file representing the contents of itself.
    # Will only create a pdf if all main attributes are present: Class, Race and Background.
    # A boolean is returned to represent if this process was a success.
    def create_pdf(self, file_path: str) -> bool:
        if self._dndClass is not None and self._background is not None and self._race is not None:
            return io.create_character_sheet(self.string_field_pdf_data(), self.button_pdf_data(),
                                             self.get_class_spells(), self.get_class_spell_slots(),
                                             self.get_prepared_or_known(), file_path)
        return False

# Function used to combine lists that elements of the character sheet share.
# Can either copy all elements or limit duplicates and supports up to three lists
# One for each element of the sheet (class, race and background)
def _combine_lists(one_list: (), two_list: (), three_list=None, duplicates=False) -> ():
    full_list = []

    # Add elements to the list if the list is not none, the item itself is not none
    # and if it complies with the duplicates clause.
    if one_list is not None:
        for item in one_list:
            if item.lower() != "none":
                if duplicates:
                    full_list.append(item)
                else:
                    if item not in full_list:
                        full_list.append(item)
    if two_list is not None:
        for item in two_list:
            if item.lower() != "none":
                if duplicates:
                    full_list.append(item)
                else:
                    if item not in full_list:
                        full_list.append(item)
    if three_list is not None:
        for item in three_list:
            if item.lower() != "none":
                if duplicates:
                    full_list.append(item)
                else:
                    if item not in full_list:
                        full_list.append(item)

    return tuple(full_list)

def _set_bool_prof_list(prof_default_names: (), prof_list: ()) -> ():
    final_list = [False for i in range(len(prof_default_names))]

    for i in range(len(prof_default_names)):
        for prof in prof_list:
            if prof.lower() == prof_default_names[i].lower():
                final_list[i] = True
                break

    return final_list

