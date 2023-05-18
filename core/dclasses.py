from dataclasses import dataclass


@dataclass()
class CycleStepInfo:
    name: str
    increment_steps: bool = False
    disable_select: bool = False
