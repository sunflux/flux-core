from clustering import messagecreator

from clustering.messagehandler import MessageHandler
from transform.recipe import Recipe, transform, placeholder


class RecipeHandler(MessageHandler):

    def __init__(self, pool, handler_config):
        MessageHandler.__init__(self, pool, handler_config)
        self._init_recipes(handler_config)

    def _init_recipes(self, recipes_config):
        self.recipes = []
        self.recipes.append(Recipe(1, ['add_time_stamp', 'add_id']))

    def handle_message(self, msg):
        msgs_bulk = msg['msgs_bulk']
        recipe = next(filter(lambda rec: rec.id == msg['recipe'], self.recipes))
        bla = self.pool.map(placeholder(recipe, msg['node_config']), msgs_bulk)
        dataset = [messagecreator.rpc_func_result('Success', bla)]
        return dataset
