from pprint import pprint


class Path:

    def __init__(self, **kwargs):
        self.args = {}
        self.responses = {}
        self.requests = {}
        self.security = []
        self.skip = False
        self.function_name = kwargs.get('function_name')
        self.path = kwargs.get('path')
        self.group = kwargs.get('group')
        self.methods = []
        self.summary = ''
        self.description = ''
        self.add_methods(kwargs.get('request_types', []))
        self.tags = []

    def add_methods(self, methods=None):
        if methods is not None:
            for x in methods:
                self.methods.append(x)

    def add_response(self, code, **kwargs):
        self.responses[code] = {}
        for k,v in kwargs.items():
            self.responses[code][k] = v

    def add_docs(self, docs):
        if docs:
            x = 0
            for s in docs.splitlines():
                s = s.strip()
                if s != '':
                    if x == 0:
                        self.summary = s
                        x += 1
                    elif x == 1:
                        if s[0:3] != '---':
                            self.description += s
                        else:
                            x += 1


