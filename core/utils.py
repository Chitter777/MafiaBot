import redis
from typing import Union


class Between:
    """
    Нахождение числа в заданном промежутке чисел
    """

    def __init__(self, n1: int, n2: int):
        self.n1 = n1
        self.n2 = n2

    def __contains__(self, item: int) -> bool:
        if self.n1 <= item <= self.n2:
            return True
        else:
            return False


class Utils:
    @staticmethod
    def calc_mafia(pl_len: int) -> int:
        """
        Вычисление нужного количества мафии для игры, согласно количеству игроков
        :param pl_len: Количество игроков в игре
        :return:
        """
        if pl_len in Between(3, 5):
            max_mafia = 1
        elif pl_len in Between(6, 9):
            max_mafia = 2
        elif pl_len in Between(10, 14):
            max_mafia = 3
        else:
            max_mafia = round(pl_len / 3)
        return max_mafia

    @staticmethod
    def match_lists(_o: list, _l: list, return_bool: bool = True) -> Union[bool, list]:
        """

        :param _o: Список, элементы которого нужно найти в другом списке.
        :param _l: Список, в котором нудно найти необходимые элементы.
        :param return_bool: Нужно ли вернуть список всех совпадений или всего лишь логическое значение.
        :return: Логиеское значение (return_bool=True), Список совпадений (return_bool=False)
        """
        if return_bool:
            for _item in _o:
                if _item in _l:
                    return True
            return False
        else:
            _response = []
            for _item in _o:
                if _item in _l:
                    _response.append(_item)
            return _response

    # @staticmethod
    # async def calc_game(data: dict):
    #     """
    #
    #     :param data: Данные, для генерации списка
    #     :return:
    #     """
