from functools import wraps
from flask_spec.path import Path
from flask_spec.schema import Schema
import types

from datetime import datetime

from pprint import pprint


class Spec:
    info = {}
    servers = []
    tags = {}
    paths = {}
    schemas = {}
    level = 0
    reserved_fields = ['string', 'object', 'array', 'type', 'required']
    skip_fields = ['name', 'schema']
    lower_case_fields = ['True', 'False']
    ret_content = ''

    def add_schema(self, name, **kwargs):
        obj = Schema()
        obj.add(name, **kwargs)
        self.schemas[name] = obj

    def set_info(self, **kwargs):
        for x in kwargs:
            self.info[x] = kwargs.get(x)

    def tag(self, tag_list):
        def api_tags(func):
            self.add_path(function_name=func.__name__)
            for x in tag_list:
                self.paths[func.__name__].tags.append(x)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return api_tags

    def set_server(self, server_list):
        if isinstance(server_list, list):
            for x in server_list:
                self.servers.append(server_list)
        elif isinstance(server_list, str):
            self.servers.append(server_list)
        # add error handling here

    def set_tag(self, name, desc):
        self.tags[name] = desc

    def request(self, method, **kwargs):
        def api_request(func):

            self.add_path(function_name=func.__name__)
            self.paths[func.__name__].add_docs(func.__doc__)
            # this will have to be redone with multiple args...
            if kwargs:
                self.paths[func.__name__].args[method] = {}
                for x in kwargs.keys():
                    self.paths[func.__name__].args[method][x] = kwargs[x]

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return api_request

    def security(self):

        def api_security(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return api_security

    def request_body(self, method, **kwargs):

        def api_requesst(func):
            self.add_path(function_name=func.__name__)
            self.paths[func.__name__].add_docs(func.__doc__)
            if kwargs:
                self.paths[func.__name__].args[method] = {}
                for x in kwargs.keys():
                    self.paths[func.__name__].args[method][x] = kwargs[x]

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return api_requesst

    def skip(self):
        def api_skip(func):
            self.add_path(function_name=func.__name__)
            self.paths[func.__name__].skip = True

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return api_skip

    def response(self, code, **kwargs):

        def api_response(func):
            self.add_path(function_name=func.__name__)
            self.paths[func.__name__].add_response(code, **kwargs)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return api_response

    def generate_path(self, func):

        func_obj = self.paths[func]

        if func_obj.args:
            for m in func_obj.args.keys():
                self.add_line(m + ':', before=1, after=1)

                if func_obj.tags:
                    self.add_line("tags:", after=1)
                    for x in func_obj.tags:
                        self.add_line("- " + x)
                    self.set_level(-1)

                if func_obj.description:
                    self.add_line('description: "' + func_obj.description + '"')

                if func_obj.summary:
                    self.add_line('summary: "' + func_obj.summary + '"')

                if func_obj.args and m == 'get':
                    self.add_line("parameters:", after=1)

                    for x in func_obj.args:
                        self.add_line("- in: path", after=1)
                        if 'name' in func_obj.args[x]:
                            self.add_line("name: " + func_obj.args[x]['name'])
                        if 'description' in func_obj.args[x]:
                            self.add_line('description: "' + func_obj.args[x]['description'] + '"')
                        if 'summary' in func_obj.args[x]:
                            self.add_line('summary: "' + func_obj.args[x]['summary'] + '"')

                        if 'required' in func_obj.args[x]:
                            self.add_line("required: " + str(func_obj.args[x]['required']).lower())
                        if isinstance(func_obj.args[x]['schema'], str):
                            self.add_line("schema:")
                            self.add_line("$ref: '#/components/schemas/" + func_obj.args[x]['schema'] + "'", before=1,
                                          after=-1)

                        else:
                            # it is the actual content
                            pass

                        self.set_level(-1)
                    self.set_level(-1)
                else:
                    self.add_line('requestBody:', after=1)
                    #HEREERERERERER


                    self.set_level(-1)

                self.add_line('responses:', after=1)

                # pprint(func_obj.responses)
                for k, v in func_obj.responses.items():

                    self.add_line("'" + str(k) + "':", after=1)

                    if 'description' in v.keys():
                        self.add_line("description: " + v['description'])
                    self.add_line("content:", after=1)

                    self.add_line("application/json:", after=1)

                    self.add_line('schema:', after=1)
                    if 'type' in v.keys():
                        self.add_line("type: " + v['type'])

                    if 'content' in v.keys():
                        self.add_line("properties:", after=1)
                        for c in v['content'].keys():
                            self.add_line(c + ":", after=1)
                            for key, value in v['content'][c].items():
                                self.add_line(key + ': ' + self.quotes(key, value))
                            self.set_level(-2)
                        self.set_level(-1)
                    elif 'schema' in v.keys():
                        self.add_line("$ref: '#/components/schemas/" + v['schema'] + "'")

                    self.set_level(-4)
                self.set_level(-1)
            self.set_level(-1)

    def set_level(self, number=0):
        self.level += number

    def add_line(self, content='', **kwargs):
        self.set_level(kwargs.get('before', 0))
        s = ''
        s += self.get_spaces()
        for x in range(0, kwargs.get('extra', 0)):
            s += ' '
        s += content + "\n"
        self.ret_content += s
        self.set_level(kwargs.get('after', 0))

    def get_spaces(self):
        s = ''
        for x in range(0, self.level * 2):
            s += ' '
        return s

    def quotes(self, check, value=None):
        if value is None:
            value = check

        quote = ''
        if check not in self.reserved_fields:
            quote = "'"

        ret = str(value)
        if ret in self.lower_case_fields:
            ret = ret.lower()

        return quote + ret + quote

    def generate_schema(self, key):
        self.add_line(key + ":", after=1)

        for k, v in vars(self.schemas[key]).items():
            if k not in self.skip_fields and v:
                # suggest: Description
                self.add_line(k + ": " + self.quotes(v))
        if self.schemas[key].schema:
            self.add_line('properties:', after=1)

            for k, v in self.schemas[key].schema.items():
                self.add_line(k + ':', after=1)

                for k2, v2 in v.items():
                    if 'enum' == k2:
                        self.add_line(k2 + ":", after=1)
                        for e in v2:
                            self.add_line("- " + self.quotes(e))


                        self.set_level(-1)

                    else:
                        self.add_line(k2 + ": " + self.quotes(k2, v2))
                self.set_level(-1)
            self.set_level(-1)
        self.set_level(-1)
        self.add_line()

    def generate_spec(self, **kwargs):
        self.index_paths(kwargs.get('app', None))

        self.add_line("openapi: 3.0.2")  # need to para this
        self.add_line("info:", after=1)

        for x in self.info:
            if 'license' == x:
                self.add_line(x + ":", after=1)

                for y in self.info[x]:
                    self.add_line(y + ": " + self.info[x][y])
                self.set_level(-1)
            else:
                self.add_line(x + ": " + self.info[x])

        self.add_line("servers:", before=-1, after=1)

        for x in self.servers:
            self.add_line("- url: " + x[0])

        self.add_line("tags:", before=-1, after=1)

        for x in self.tags:
            self.add_line("- name: " + x)

            self.add_line("description: " + self.tags[x], before=1, after=-1)

        self.add_line("paths:", before=-1, after=1)

        for x in self.paths.keys():
            if self.paths[x].skip != True and self.paths[x].path != '/static/<path:filename>':
                self.add_line(self.paths[x].path.replace('<', '{').replace('>', '}') + ":")
                self.generate_path(x)

        self.add_line("components:", before=-2, after=2)

        self.add_line("schemas:", after=1)

        for x in self.schemas:
            self.generate_schema(x)
        self.set_level(-2)

        self.generate_file(kwargs.get('file', 'api.yaml'))

    def generate_file(self, file_name):
        file = open(file_name, 'w')
        file.write(self.ret_content)
        file.close()

    def add_path(self, **kwargs):
        function_name = kwargs.get('function_name')

        if function_name in self.paths.keys():
            self.update_path(**kwargs)
        else:
            self.paths[function_name] = Path(function_name=function_name,
                                             path=kwargs.get('path'),
                                             request_types=kwargs.get('request_types'),
                                             group=kwargs.get('group'))

    def update_path(self, **kwargs):
        function_name = kwargs.get('function_name')
        self.paths[function_name].path = kwargs.get('path')
        self.paths[function_name].group = kwargs.get('group')
        self.paths[function_name].add_methods(kwargs.get('request_types', []))

    def index_paths(self, app):
        for rule in app.url_map.iter_rules():
            if len(rule.endpoint.split(".")) > 1:
                group, function_name = rule.endpoint.split('.')
                self.add_path(
                    function_name=function_name,
                    path=str(rule),
                    request_types=rule.methods,
                    group=group
                )
            else:
                self.add_path(
                    function_name=rule.endpoint,
                    path=str(rule),
                    request_types=rule.methods,
                )
