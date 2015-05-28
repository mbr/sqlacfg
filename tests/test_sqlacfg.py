import pytest
from sqlacfg import ConfigSettingMixin, Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
Session = sessionmaker()


class ConfigSetting(Base, ConfigSettingMixin):
    __tablename__ = 'config'


@pytest.fixture
def engine():
    return create_engine('sqlite:///:memory:', echo=True)


@pytest.fixture
def session(engine):
    return Session(bind=engine)


@pytest.fixture
def bare_cfg(engine, session):
    Base.metadata.create_all(bind=engine)

    return Config(ConfigSetting, session)


@pytest.fixture
def cfg(bare_cfg):
    c = bare_cfg
    c['base']['key_a'] = 123
    c['base']['key_b'] = 'KEY B'
    c['other']['key_a'] = 456

    return c


def test_nonexistant_key(cfg):
    with pytest.raises(KeyError):
        # with existing section
        cfg['base']['does_not_exist']

    with pytest.raises(KeyError):
        # with nonexisting section
        cfg['no_way_jose']['does_not_exist']


def test_existing_key(cfg):
    assert cfg['base']['key_a'] == 123
    assert cfg['base']['key_b'] == 'KEY B'


def test_no_sections(bare_cfg):
    assert bare_cfg.sections() == set({})


def test_sections(cfg):
    assert {'base', 'other'} == cfg.sections()


def test_sections_contains(cfg):
    assert 'base' in cfg
    assert 'dne' not in cfg


def test_get(cfg):
    assert cfg['base'].get('key_a') == 123
    assert cfg['base'].get('dne', 56) == 56


def test_contains(cfg):
    assert 'key_a' in cfg['base']
    assert 'dne' not in cfg['base']


def test_iteritems(cfg):
    assert dict(cfg['base'].iteritems()) == {'key_a': 123,
                                             'key_b': 'KEY B'}
