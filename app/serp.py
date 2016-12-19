# search engine results page
from framework.request_handler import ThermostHouseRequestHandler
from google.appengine.api import search


class SearchRecipes(ThermostHouseRequestHandler):
    def get(self):
        query = self.request.get('q')

        if not query:
            self.redirect('/')
        else:
            index = search.Index('recipes')
            # create string snippet on direction field with 140 characters
            snippet = 'snippet("%s", directions, 140)' % query

            options = search.QueryOptions(
                returned_expressions=[
                    search.FieldExpression(name='snippet', expression=snippet)
                ]
            )

            results = index.search(
                query=search.Query(
                    query_string=query,
                    options=options
                )
            )

            docs = []  # empty list
            if results:
                docs = results.results

            tpl_values = {
                'recipes': docs,
                'query': query
            }

            self.render('/serp/serp.html', **tpl_values)
