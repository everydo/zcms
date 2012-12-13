#-*- encoding:utf-8 -*-
import datetime
from types import TupleType, ListType
import decimal
from json import JSONEncoder, JSONDecoder


class AwareJSONEncoder(JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time types
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, str):
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
            return super(AwareJSONEncoder, self).default(o)


class AwareJSONDecoder(JSONDecoder):
    """
    JSONEncoder subclass that knows how to encode date/time types
    """

    def __init__(self, encoding=None, object_hook=None):
        if object_hook is None:
            object_hook = self.json_to_python
        JSONDecoder.__init__(self, encoding, object_hook)

    def json_to_python(self, d):
        if '__datetime__' in d:
            if d['value'] is None:
                return None
            strp = time.strptime(d['value'], self.DATETIME_FMT)[:7]
            return datetime.datetime(*strp)
        if '__date__' in d:
            if d['value'] is None:
                return None
            strp = time.strptime(d['value'], self.DATE_FMT)[:3]
            return datetime.date(*strp)
        if '__time__' in d:
            if d['value'] is None:
                return None
            strp = time.strptime(d['value'], self.TIME_FMT)[3:6]
            return datetime.time(*strp)
        if '__decimal__' in d:
            if d['value'] is None:
                return None
            return decimal.Decimal(d['value'])
        return d
