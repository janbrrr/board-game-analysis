class NoEntriesFoundException(Exception):
    def __init__(self, *args, **kwargs):

        Exception.__init__(self, *args, **kwargs)


class TooManyPagesException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)