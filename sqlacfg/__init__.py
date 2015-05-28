import json

from sqlalchemy import Column, String, distinct


__version__ = '0.2'


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


class Config(object):
    def __init__(self, model, session):
        self.model = model
        self.session = session

    def sections(self):
        return set(s for (s,) in
                   self.session.query(distinct(self.model.section)))

    def __contains__(self, key):
        return (self.session.query(self.model)
                .filter(self.model.section == key)
                .limit(1)
                .first()) is not None

    def __getitem__(self, key):
        # return a specific section
        return ConfigSection(self.model, self.session, key)


class ConfigSection(object):
    def __init__(self, model, session, section):
        self.model = model
        self.session = session
        self.section = section

    def __contains__(self, key):
        return bool(self.session.query(self.model).get((key, self.section)))

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, *d):
        if len(d) > 1:
            raise TypeError('Only one extra argument allowed')

        cs = self.session.query(self.model).get((key, self.section))

        if cs is not None:
            # we found a record
            return cs.value

        # return default
        if d:
            return d[0]

        raise KeyError(key)

    def __setitem__(self, key, value):
        cs = self.session.query(self.model).get((key, self.section))
        if cs is None:
            cs = self.model(key=key, value=value, section=self.section)
        else:
            cs.value = value

        self.session.add(cs)

    def iteritems(self):
        for rec in self.session.query(self.model).filter_by(
            section=self.section
        ):
            yield (rec.key, rec.value)
