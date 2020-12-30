

class FlowException(Exception):
    """Base Exception class for sqla-flow"""


class FlowQueryException(FlowException):
    def __init__(self):
        raise FlowException("Missing query method. Did you set query on FlowBase?")