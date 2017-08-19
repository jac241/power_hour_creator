import logging
import os
import sys
from glob import glob

from PyQt5.QtWidgets import QMessageBox

from power_hour_creator import config
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


def ensure_log_folder_exists():
    os.makedirs(config.APP_DIRS.user_log_dir, exist_ok=True)


def setup_logging():
    ensure_log_folder_exists()
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=os.path.join(
                            config.APP_DIRS.user_log_dir,
                            '{}.log'.format(config.phc_env)),
                        filemode='a')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root _logger
    root_logger = logging.getLogger('')

    if len(root_logger.handlers) < 1: # this gets called
        root_logger.addHandler(console)


def connect_to_db():
    logger = logging.getLogger(__name__)
    logger.info('Connecting to DB: {}'.format(config.db_path()))
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(config.db_path())

    if not db.open():
        QMessageBox.critical(
            None,
            'Cannot open database',
            'Unable to open database\n\nClick Cancel to exit',
            QMessageBox.Cancel
        )

    return db


class MigrationError(Exception):
    pass


def ensure_migrations_table_exists():
    query = QSqlQuery()
    # noinspection SqlNoDataSourceInspection
    result = query.exec_("""
        CREATE TABLE IF NOT EXISTS migrations (
            level INTEGER PRIMARY KEY
        );
    """)


def fail_migration(query, migration):
    QSqlDatabase.database().rollback()
    QMessageBox.critical(
        None,
        'Migration failed',
        (
            'Migration {} failed with error {}'
            '\n\nClick Cancel to exit'
        ).format(migration.path, query.lastError().databaseText()),
        QMessageBox.Cancel
    )
    raise MigrationError


def update_schema_migrations_level(migration):
    query = QSqlQuery()
    query.prepare("INSERT INTO migrations (level) VALUES (:level)")
    query.bindValue(':level', migration.level)
    if not query.exec_():
        fail_migration(query, migration.path)


def get_migration_level():
    query = QSqlQuery()
    query.exec_("SELECT MAX(level) FROM migrations")

    level = None
    while query.next():
        level = query.value(0)

    return level or 0

from functools import update_wrapper
class reify(object):
    """ Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.  The following is an example and
    its usage:

    .. doctest::

        >>> from pyramid.decorator import reify

        >>> class Foo(object):
        ...     @reify
        ...     def jammy(self):
        ...         print('jammy called')
        ...         return 1

        >>> f = Foo()
        >>> v = f.jammy
        jammy called
        >>> print(v)
        1
        >>> f.jammy
        1
        >>> # jammy func not called the second time; it replaced itself with 1
        >>> # Note: reassignment is possible
        >>> f.jammy = 2
        >>> f.jammy
        2
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class Migration:
    def __init__(self, path):
        self.path = path

    @reify
    def level(self):
        filename = os.path.basename(self.path)
        return int(os.path.splitext(filename)[0])

    def already_performed(self, other_level):
        return self.level <= other_level


def log_attempting_migration(migration):
    logger = logging.getLogger(__name__)
    logger.info('Migrating DB to level {}'.format(migration.level))


def log_successful_migration(migration):
    logger = logging.getLogger(__name__)
    logger.info('Successfully migrated DB to level {}'.format(migration.level))


def migrate_database():
    initial_migration_level = get_migration_level()
    migration_paths = glob(os.path.join(config.MIGRATIONS_PATH, '*.sql'))

    for migration in map(lambda p: Migration(p), sorted(migration_paths)):

        if migration.already_performed(initial_migration_level):
            continue

        with open(migration.path, 'r') as f:
            QSqlDatabase.database().transaction()

            log_attempting_migration(migration)

            for statement in f.read().split(';'):
                query = QSqlQuery()
                if not query.exec_(statement):
                    fail_migration(query, migration)

            update_schema_migrations_level(migration)
            QSqlDatabase.database().commit()

            log_successful_migration(migration)


def setup_database():
    ensure_db_folder_exists()
    connect_to_db()
    ensure_migrations_table_exists()
    migrate_database()


def ensure_db_folder_exists():
    os.makedirs(config.APP_DIRS.user_data_dir, exist_ok=True)


def bootstrap_app():
    setup_logging()
    setup_database()

