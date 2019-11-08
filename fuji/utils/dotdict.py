class dotdict(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(*args):
        val = dict.get(*args)
        if type(val) is dict:
            return dotdict(val)
        elif type(val) is list:
            return [dotdict(obj) if type(obj) is dict else obj for obj in val]
        else:
            return dotdict(val) if type(val) is dict else val
