#-*- encoding:utf-8 -*-
import datetime
from types import TupleType,ListType
import decimal
from json import JSONEncoder,JSONDecoder
from zope.datetime import parseDatetimetz

class AwareJSONEncoder(JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time types
    """
    
    DATE_FORMAT = "%Y-%m-%d" 
    TIME_FORMAT = "%H:%M:%S"
    
    def default(self, o):
        if isinstance(o,str):
            return o
        elif isinstance(o, datetime.datetime):
            return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            return o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(AwareJSONEncoder,self).default(o)

class AwareJSONDecoder(JSONDecoder):
    """
    JSONEncoder subclass that knows how to encode date/time types
    """

    def __init__(self, encoding=None, object_hook=None):
        if object_hook is None:
            object_hook = self.json_to_python
        JSONDecoder.__init__(self, encoding, object_hook)
    
    
    def json_to_python(self, d):
        for key in d:
            if key in ['created','modified','effective']:
               d[key] = parseDatetimetz(d[key])
            if isinstance(d[key],str):
                d[key] = unicode(d[key])
            if type(d[key]) in [ListType,TupleType]:
                d[key] = map(unicode,d[key])

        return d


