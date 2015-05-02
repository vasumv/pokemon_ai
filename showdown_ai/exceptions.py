class ShowdownException(Exception):
    pass

class UserNotOnlineException(ShowdownException):
    pass

class TierException(ShowdownException):
    pass

class GameOverException(ShowdownException):
    pass
