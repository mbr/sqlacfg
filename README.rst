sqlacfg
=======

Allows you to store configuration in an SQLAlchemy_ database instead of
configuration files. The API is close, but not exactly like ``configparser``
and it plugs right into any application that is already using a declarative
SQLAlchemy_ model:

.. code-block::

   # create a new model to hold the configuration items
   class ConfigSetting(Base, ConfigSettingMixin):
       __tablename__ = 'configuration'

   # instantiate the model with your session
   config = Config(ConfigSetting, session)

   # now config sections will work like a regular dict
   config['section_foo']['bar'] = 123

   # values will be json-encoded before being stored (this can be changed)
   # to persist changes, simply commit the session
   session.commit()


A full, minimal example is a bit more verbose due to the required initial
setup:


.. code-block::

   from sqlacfg import ConfigSettingMixin, Config
   from sqlalchemy import create_engine
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import sessionmaker

   Base = declarative_base()
   Session = sessionmaker()

   class ConfigSetting(Base, ConfigSettingMixin):
       __tablename__ = 'configuration'


   # for this demonstration, we just create the db in memory
   eng = create_engine('sqlite:///:memory:', echo=True)
   Base.metadata.create_all(eng)

   session = sessionmaker(bind=eng)()

   config = Config(ConfigSetting, session)

   config['base']['foo'] = 'bar'
   config['base']['baz'] = 'baz'

   print dict(config['base'].iteritems())



.. _SQLAlchemy: http://www.sqlalchemy.org/
