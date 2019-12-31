class Choices(object):
    @classmethod
    def choices(cls):
        d = cls.__dict__
        return {item: d[item] for item in d.keys() if not item.startswith('__')}

