from functools import partial
from transform import funcs

from clustering import messagecreator


class Recipe(object):

    def __init__(self, recipe_id, funcs_config):
        self.id = recipe_id
        self.operations = []
        self.__init_operations(funcs_config)

    def __init_operations(self, funcs_config):
        for func_config in funcs_config:
            func = getattr(funcs, func_config)
            self.operations.append(func)


def transform(recipe, config, record):
    for func in recipe.operations:
        record = func(config, record)
    return record
    #return messagecreator.rpc_func_result('Success', record)


def placeholder(recipe, config):
    return partial(transform, recipe, config)


####EXAMPLE####
from multiprocessing import Pool

#pool = Pool(4)
#pool.map(placeholder, [])
