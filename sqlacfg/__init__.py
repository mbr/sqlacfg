from collections import MutableMapping, Mapping
import json

from sqlalchemy import Column, String, distinct


__version__ = '0.3'


class ConfigSettingMixin(object):
    _cfg_serializer = staticmethod(json.dumps)
    _cfg_deserializer = staticmethod(json.loads)

    @property
    def value(self):
        return self._cfg_deserializer(self.data)

    @value.setter
    def value(self, v):
        self.data = self.__class__._cfg_serializer(v)

    key = Column(String, primary_key=True)
    section = Column(String, primary_key=True)
    data = Column(String, nullable=True)


class Config(Mapping):
    def __init__(self, model, session):
        self.model = model
        self.session = session

    def __iter__(self):
        for (section,) in self.session.query(distinct(self.model.section)):
            yield section

    def __len__(self):
        return self.session.query(distinct(self.model.section)).count()

    def sections(self):
        return set(s for s in self)

    def __contains__(self, key):
        return bool(self.session.query(self.model.section)
                                .filter_by(section=key).first())

    def __getitem__(self, key):
        # return a specific section
        return ConfigSection(self.model, self.session, key)

    def resolve(self, name):
        split = name.index('.')
        return self[name[:split]], name[split+1:]

    def cget(self, name):
        section, key = self.resolve(name)
        return section[key]

    def cset(self, name, value):
        section, key = self.resolve(name)
        section[key] = value

    def cdel(self, name):
        section, key = self.resolve(name)
        del section[key]


class ConfigSection(MutableMapping):
    def __init__(self, model, session, section):
        self.model = model
        self.session = session
        self.section = section

    @property
    def _all(self):
        return self.session.query(self.model).filter_by(section=self.section)

    def __getitem__(self, key):
        cs = self.session.query(self.model).get((key, self.section))

        if cs is None:
            raise KeyError(key)

        return cs.value

    def __setitem__(self, key, value):
        cs = self.session.query(self.model).get((key, self.section))
        if cs is None:
            cs = self.model(key=key, value=value, section=self.section)
        else:
            cs.value = value

        self.session.add(cs)

    def __delitem__(self, key):
        rc = self.session.query(self.model).filter_by(
            key=key,
            section=self.section
        ).delete()

        if not rc:
            raise KeyError(key)

    def __iter__(self):
        for (k,) in self.session.query(self.model.key).all():
            yield k

    def __len__(self):
        return self._all.count()

    # for greater efficiency, item-iteration and value-iteration is implemented
    # directly
    def iteritems(self):
        for rec in self._all:
            yield (rec.key, rec.value)

    def items(self):
        return list(i for i in self.iteritems())

    def itervalues(self):
        for rec in self._all:
            yield rec.value

    def values(self):
        return list(i for i in self.itervalues())
