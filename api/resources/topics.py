from flask_restful import Resource


class Topics(Resource):
    def __init__(self, **kwargs):
        self.topics = kwargs['topics']

    def get(self):
        return {'topics': self.topics}
