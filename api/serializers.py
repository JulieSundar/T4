from flask_restplus import fields
from T4.api import api

log_post = api.model('log post', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a log post'),
    'title': fields.String(required=True, description='Article title'),
    'body': fields.String(required=True, description='Article content'),
    'pub_date': fields.DateTime,
    'end_date': fields.DateTime,
    'category_id': fields.Integer(attribute='category.id'),
    'category': fields.String(attribute='category.id'),
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_log_posts = api.inherit('Page of log posts', pagination, {
    'items': fields.List(fields.Nested(log_post))
})

category = api.model('log category', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a log category'),
    'name': fields.String(required=True, description='Category name'),
})

category_with_posts = api.inherit('log category with posts', category, {
    'posts': fields.List(fields.Nested(log_post))
})
