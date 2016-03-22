import simplejson as json

class JsonSerializer():
    def dumps(self, obj):
        return json.dumps(obj).encode('ascii')

    def loads(self, data):
        return json.loads(data.decode('ascii'))
