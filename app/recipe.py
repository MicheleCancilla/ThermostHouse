from framework.request_handler import ThermostHouseRequestHandler
from google.appengine.api import search
from models.recipes import Recipes


class RecipePage(ThermostHouseRequestHandler):
    def get(self, recipe_id):  # must be there because is in url and not in the header
        recipe = Recipes.get_by_id(int(recipe_id)) #  because recipe_id was a string

        template_values = {
            'recipe': recipe
        }

        self.render('recipe-page/recipe-page.html', **template_values)
