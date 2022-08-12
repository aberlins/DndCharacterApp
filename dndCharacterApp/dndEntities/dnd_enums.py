# Module which contains two enums that are used in the application: Gender and Alignment

import enum


class Gender(enum.Enum):
    Male = "Male"
    Female = "Female"

    def __str__(self):
        return self.value


class Alignment(enum.Enum):
    Lawful_Good = "Lawful", "Good"
    Neutral_Good = "Neutral", "Good"
    Chaotic_Good = "Chaotic", "Good"
    Lawful_Neutral = "Lawful", "Neutral"
    True_Neutral = "Neutral", "Neutral"
    Chaotic_Neutral = "Chaotic", "Neutral"
    Lawful_Evil = "Lawful", "Evil"
    Neutral_Evil = "Neutral", "Evil"
    Chaotic_Evil = "Chaotic", "Evil"

    # Returns the enum's Lawful/Chaotic Axis Value
    def lc_axis_value(self) -> str:
        return self.value[0]

    # Returns the enum's Good/Evil Axis Value
    def ge_axis_value(self) -> str:
        return self.value[1]

    # String method will return the full Alignment name
    def __str__(self):
        if self == Alignment.True_Neutral:
            return "True Neutral"
        else:
            return self.value[0] + " " + self.value[1]