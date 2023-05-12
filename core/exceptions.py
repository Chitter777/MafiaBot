class AllVoted(Exception):
    """
    Исключение вызывается, если все проголосовали
    """

    def __init__(self, message):
        self.message = message
