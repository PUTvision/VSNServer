__author__ = 'Amin'


def enum(**enums):
    return type('Enum', (), enums)
