from flask_restful import Resource


class Posts(Resource):
    def __init__(self, **kwargs):
        self.top_posts = kwargs['top_posts']

    def get(self, topic):
        posts = [post._asdict() for post in self.top_posts[topic]]
        return {'posts': posts}
