from enum import Enum, IntFlag, auto
from core import CycleStepInfo


s = " делает свой выбор"


class PlayerRole(IntFlag):
    INNOCENT = auto()
    DEAD = auto()
    ARRESTED = auto()
    DETECTIVE = auto()
    MEDIC = auto()
    HARLOT = auto()  # Ночная бабочка
    MANIAC = auto()
    MAFIA = auto()
    SENIOR = auto()  # он же Дон мафии


class PlayerRoleName(Enum):
    INNOCENT = "Мирный житель"
    DEAD = "Мёртвый"
    ARRESTED = "Арестованный"
    DETECTIVE = "Детектив"
    MEDIC = "Медик"
    HARLOT = "Путана"
    MANIAC = "Маньяк"
    MAFIA = "Мафия"
    SENIOR = "Дон мафии"

    @classmethod
    def get_key(cls, value):
        for key, val in cls.__members__.items():
            if val.value == value:
                return key
        return None


class PlayerRoleEmoji(Enum):
    INNOCENT = "👥"
    DEAD = "💀"
    ARRESTED = "⛓"
    DETECTIVE = "🔎"
    MEDIC = "🩺"
    HARLOT = "👠"
    MANIAC = "🔪"
    MAFIA = "🎩"
    SENIOR = "🚬"
    HARLOT_EFFECT = "💞"

    @classmethod
    def get_key(cls, value):
        for key, val in cls.__members__.items():
            if val.value == value:
                return key
        return None


class EnabledPlayerRoles(IntFlag):
    DETECTIVE = auto()
    MEDIC = auto()
    HARLOT = auto()
    MANIAC = auto()
    SENIOR = auto()


class ChosenType(IntFlag):
    ARREST = auto()  # назначен на арест
    HEAL = auto()  # вылечен (имеет иммунитет от убийства мафией)
    HEALED = auto()  # был вылечен и не может быть вылечен далее
    HARLOT = auto()  # ночная бабочка стоит у порога
    HARLOTTED = auto()  # ночная гостья уже была у игрока в гостях


class ChoiceType(IntFlag):
    HARLOT_CHOSE = auto()
    MAFIA_KILL = auto()
    SENIOR_CHECK = auto()
    DETECTIVE_CHECK = auto()
    MEDIC_CHOSE = auto()
    MANIAC_KILL = auto()


class CycleTimer(Enum):
    NIGHT_GREETINGS = CycleStepInfo("Ознакомительная ночь")
    DAY_GREETINGS = CycleStepInfo("Ознакомительный день", True)
    NIGHT_MAFIA = CycleStepInfo("Мафия " + s, True)
    NIGHT_SENIOR = CycleStepInfo("Дон мафии" + s)
    NIGHT_MEDIC = CycleStepInfo("Медик" + s)
    NIGHT_HARLOT = CycleStepInfo("Путана" + s)
    NIGHT_DETECTIVE = CycleStepInfo("Детектив" + s)
    NIGHT_MANIAC = CycleStepInfo("Маньяк" + s)
    DAY_PREVOTE = CycleStepInfo("Дневное обсуждение", True, True)
    DAY_VOTE = CycleStepInfo("Дневное голосование")
