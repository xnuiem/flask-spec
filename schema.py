from pprint import pprint


class Schema:


    def __init__(self):
        self.name = None
        self.schema = {}
        self.type = None
        self.description = None
        self.example = None
        self.required = []

    def add(self, name, **kwargs):

        self.name = name
        self.type = kwargs.get('type', None)
        self.description = kwargs.get('description', None)

        if self.type == 'string':
            self.example = kwargs.get('example', None)

        elif self.type == 'object':
            content = kwargs.get('content', {})
            if content:
                for x in content.keys():
                    self.schema[x] = content[x]

