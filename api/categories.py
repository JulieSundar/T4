import logging

from flask import request
from flask_restplus import Resource

from T4.api import api
from T4.api.serializers import category, category_with_posts
from T4.posts.services import create_category, delete_category, update_category
from T4.posts.models import Category

log = logging.getLogger(__name__)

ns = api.namespace('log/categories', description='Operations related to T4 log categories')


@ns.route('/')
class CategoryCollection(Resource):

    @api.marshal_list_with(category)
    def get(self):
        """
        Returns list of log categories.
        """
        categories = Category.query.all()
        return categories

    @api.response(201, 'Category successfully created.')
    @api.expect(category)
    def post(self):
        """
        Creates a new log category.
        """
        data = request.json
        create_category(data)
        return None, 201


@ns.route('/<int:id>')
@api.response(404, 'Category not found.')
class CategoryItem(Resource):

    @api.marshal_with(category_with_posts)
    def get(self, id):
        """
        Returns a category with a list of posts.
        """
        return Category.query.filter(Category.id == id).one()

    @api.expect(category)
    @api.response(204, 'Category successfully updated.')
    def put(self, id):
        """
        Updates a log category.

        Use this method to change the name of a log category.

        * Send a JSON object with the new name in the request body.

        ```
        {
          "name": "New Category Name"
        }
        ```

        * Specify the ID of the category to modify in the request URL path.
        """
        data = request.json
        update_category(id, data)
        return None, 204

    @api.response(204, 'Category successfully deleted.')
    def delete(self, id):
        """
        Deletes log category.
        """
        delete_category(id)
        return None, 204
