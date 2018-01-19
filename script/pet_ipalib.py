import re
from datetime import datetime
from types import MethodType, SliceType

class IpaMmlItem:
    """ base class for items contained in CommonDict """
    def __str__(self):
        """ support a nice string representation with all attribute values"""
        tmp = "\n".join(sorted([ "%s=%s" % (item, getattr(self, item)) for item in dir(self)
                                if not item.startswith("_") and getattr(self, item) != None and
                                    type(getattr(self, item)) is not MethodType ] ))
        for i in range(len(tmp)):
            if ord(tmp[i]) > 127:
                tmp = tmp.replace(tmp[i], " ")
        return str(self.__class__.__name__) + ':\n{\n' + tmp + '}\n'

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()


class IpaMmlDict(dict):
    """ A specialization of generic python dict with the following extensions/differences:
    - if a key/index does not exits Common dict will not raise KeyError but return None
    - may be used like a list an element is addressed via an integer as index
      (does not work if you use integers as keys)
    - support a list of keys in the order they have been inserted: ordered_keys
    - supporting sorting of this ordered_keys attribute and thus the "list" CommonDict itself
    - nice string representation also if objects are contained
    - contained object should be derived from CommonItem (not mandatory)
    """
    def __init__(self,*args):
        """ should also be called by subclasses,
        otherwise you might have problems with empty CommonDicts when the attribute ordered_keys is not present
        """
        dict.__init__(self,*args)
        self.ordered_keys = []

    def __str__(self):
        """ support a nice string representation """
        try:
            tmp = "\n".join([  '%s:[%s]' %(str(key), str(self[key])) for key in self.ordered_keys ])
            # tmp = "\n".join([ str(key) + ':' + str(self[key]) for key in self.ordered_keys ])
            for i in range(len(tmp)):
                if ord(tmp[i]) > 127:
                    tmp = tmp.replace(tmp[i], " ")
            return tmp
        except AttributeError:
            return ""

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()

    def __getitem__(self, key):
        """ access the item identified by key, either behave like a dictionary or like a list
        return None is no item is found
        """
        if len(self)==0:
            return None
        try:
            return dict.__getitem__(self,key)
        except KeyError:
            pass
        if type(key) == type(1):
            try:
                return dict.__getitem__(self, self.ordered_keys[key])
            except IndexError:
                pass
        return None

    def __setitem__(self, key, item):
        """ store the new item in the dictionary and append the key to ordered_list """
        #if type(key) == type(1):
        #    raise RuntimeError("CommonDict does not support integer as key")
        dict.__setitem__(self, key, item)
        try:
            if key in self.ordered_keys:
                self.ordered_keys.remove(key)
            self.ordered_keys.append(key)
        except AttributeError:
            self.ordered_keys = [key, ]

    def __delitem__(self, key):
        """ remove the new item from the dictionary and remove the key from ordered_list,
        works both with key and index """
        try:
            dict.__delitem__(self, key)
            self.ordered_keys.remove(key)
        except KeyError:
            if type(key) == type(1):
                dict.__delitem__(self, self.ordered_keys[key])
                del(self.ordered_keys[key])


    def __getattr__(self, name):
        """ support direct access to the item's attributes if only a single item is contained """
        if len(self) != 1:
            raise AttributeError
        return getattr(self.values()[0], name)

    def length(self):
        """ only because x.length() looks nicer than x.__len__()"""
        return len(self)

    def _get_empty_container(self):
        """ needed so that select_entries_from_list can return the correct type of container,
        can be overwritten by subclasses """
        return CommonDict()

    def sort(self,*args):
        """ sorts attribute orderd_keys and thus also CommonDict itself if used as a list
        can be overwritten by subclasses if a special sorting algortihm is needed. """
        try:
            self.ordered_keys.sort(*args)
        except AttributeError:
            pass


class KeywordGroup(IpaMmlDict):

    def __init__(self):
        IpaMmlDict.__init__(self)
        time_now = datetime.now()
        self.id = time_now.strftime(
            '%Y%m%d%H%M%S') + ('%03d' % time_now.microsecond)[:3]

    def append(self, kw_name, *args):
        from robot.libraries import BuiltIn
        builtin = BuiltIn.BuiltIn()
        item = KeywordItem()
        item.name = kw_name
        item.args = list(args)
        try:
            result = builtin.run_keyword(kw_name, *args)
            item.status = 'PASS'
            item.result = result
        except Exception, e:
            item.status = 'FAILED'
            item.result = e
        item.end_time = datetime.now()
        self['%d' % len(self)] = item

    def __str__(self):
        return 'keywordgroup%s' % self.id


class KeywordItem(IpaMmlItem):

    def __init__(self):
        self.name = ''
        self.args = []
        self.result = None
        self.status = None
        self.start_time = datetime.now()
        self.end_time = None


def init_keyword_group():
    '''
    This keyword is used to initialize a keyword group, it should be used together with "Run Keyword In Group" and "Finish Keyword Group"
    | Input Paramaters | Man. | Description |

    Return:
    An instance of KeywordGroupDict

    Example:
    | ${group} | Init Keyword Group |
    '''
    return KeywordGroup()


def run_keyword_in_group(group, kw_name, *args):
    '''
    This keyword is used to run keyword in a specified group, it should be used together with "Init Keyword Group" and "Finish Keyword Group"
    | Input Paramaters | Man. | Description |
    | group            | Yes  | return value of kw "Init Keyword Group" |
    | kw_name          | Yes  | keyword name like "get Units" |
    | *args            | No   | arguments list of kw_name  |

    Return:
    None

    Example:
    | ${group} | Init Keyword Group | | |
    | Run Keyword In Group | ${group} | Specified Computer Logs Should Not Be Found | OMU |
    | Run Keyword In Group | ${group} | No Critical And Hw Related Alarms Should Be Active For Specified Units | NPS1-0 |
    | Run Keyword In Group | ${group} | Restart System | |
    '''
    group.append(kw_name, *args)


def finish_keyword_group(group):
    '''
    This keyword is used to verify the keyword group's result, it should be used together with "Init Keyword Group" and "Run Keyword In Group".
    If any of keyword in group fails, it will raise an AssertionError.
    | Input Paramaters | Man. | Description |
    | group            | Yes  | return value of kw "Init Keyword Group" |

    Return:
    None

    Example:
    | ${group} | Init Keyword Group | | |
    | Run Keyword In Group | ${group} | Specified Computer Logs Should Not Be Found | OMU |
    | Run Keyword In Group | ${group} | No Critical And Hw Related Alarms Should Be Active For Specified Units | NPS1-0 |
    | Run Keyword In Group | ${group} | Restart System | |
    | Finish Keyword Group | ${group} |  |  |
    '''
    error_list = []
    for item in sorted(group.values(), key=lambda x: x.start_time):
        if item.status == 'FAILED':
            msg = ''
            if isinstance(item.result, basestring):
                msg = item.result
            elif isinstance(item.result, list) or isinstance(item.result, tuple):
                msg = '\n'.join([str(e) for e in item.result])
            elif isinstance(item.result, dict):
                msg = str(item.result)
            else:
                msg = str(item.result)
            error_msg = 'Failed keyword: "%s"\nStart: %s, End: %s, Duration: %s\nError message: %s\n' % (
                item.name, item.start_time, item.end_time, (item.end_time - item.start_time), msg)
            error_list.append(error_msg)

    if error_list:
        # raise Exception, '\n'.join(error_list)
        raise AssertionError('\n'.join(error_list))


if __name__ == '__main__':
    print 'OK'