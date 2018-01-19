from petbase import *

class event(object):
    def __init__(self, name='', piority=50):
        self.name       = name
        self.piority    = piority

    def __repr__(self):
        return '%s                 %d' %(self.name, self.piority)

class testObject(object):
    def __init__(self, name='', index = 0, alias = 'default'):
        self.name = name
        self.index = index
        self.alias = alias
        self.parent = None
        self.subtos = []
        self.events = []
        for eventname in  [x for x in dir(self) if x.startswith('on')]:
            self.events.append(event(eventname))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()

    def set_piority(self, eventname, new_piority):
        event = [x for x in self.events if x.name.upper() == eventname.upper()]
        if event:
            event[0].piority = new_piority

    def attach_subto(self, subto):
        self.subtos.append(subto)

    def show_event_map(self):
        for event in self.events:
            print event

    def show_subto(self):
        for to in self.subtos:
            print to

class toEnv(testObject):
    def __init__(self):
        super(toEnv, self).__init__('TaEnv')

    def onSuiteSetup(self):
        print 'work on env suite setup'

    def onCaseSetup(self):
        print 'work on env case setup'

    def onCaseTeardown(self):
        print 'work on env case teardown'

    def onSuiteTeardown(self):
        print 'work on env Suite Teardown'


class toBts(testObject):
    def __init__(self, btsid):
        super(toBts, self).__init__('BTS' + str(btsid))

    def onSuiteSetup(self):
        print 'work on bts suite setup'

    def onCaseSetup(self):
        print 'work on bts case setup'

    def onCaseTeardown(self):
        print 'work on bts case teardown'

    def onSuiteTeardown(self):
        print 'work on bts Suite Teardown'

class toTM500(testObject):
    def onCaseSetup(self):
        print 'work on TM500 case setup'

    def onCaseTeardown(self):
        print 'work on TM500 case teardown'



def run_to_event(to, eventname):
    if eventname in [event.name for event in to.events]:
        getattr(to, eventname)()

    for piority in range(100):
        for subto in to.subtos:
            events = [x for x in subto.events if x.name == eventname and x.piority == piority]
            for event in events:
                run_to_event(subto, eventname)

def run_to_event_reverse(to, eventname):
    for piority in range(100):
        for subto in to.subtos:
            events = [x for x in subto.events if x.name == eventname and x.piority == piority]
            for event in events:
                run_to_event_reverse(subto, eventname)
    if eventname in [event.name for event in to.events]:
        getattr(to, eventname)()

root = testObjesct('PET TA Case')

tom = toEnv()
tom.set_piority('onSuiteSetup', 3)
# tom.show_event_map()

bts1 = toBts('1234')
bts2 = toBts('1601')

tm500 = toTM500('229')

root.attach_subto(tom)
root.attach_subto(bts1)
root.attach_subto(tm500)
root.attach_subto(bts2)

tm500.set_piority('onCaseSetup', 3)

# root.show_subto()

run_to_event(root, 'onCaseSetup')

