from power_hour_creator.ui.helpers import store_results_in_settings, \
    store_dirname_in_settings
from tests.support.mocks import MockSettings


def test_store_result_should_store_results_in_settings():
    settings = MockSettings()

    @store_results_in_settings(key='k', settings=settings)
    def f():
        return 45

    f()
    assert settings.value('k') == 45


def test_store_result_should_let_you_transform_the_result_before_storing():
    settings = MockSettings()
    double = lambda x: x + x

    @store_results_in_settings(key='k', settings=settings, transform=double)
    def f():
        return 10

    f()
    assert settings.value('k') == 20


def test_store_dirname_in_settings_stores_the_resulting_dir_in_settings():
    settings = MockSettings()

    @store_dirname_in_settings(key='d', settings=settings)
    def f():
        return '/test/file.json'

    f()
    assert settings.value('d') == '/test'


def test_store_dirname_returns_the_old_value_if_no_new_value():
    settings = MockSettings({'k': '/old/dir'})

    @store_dirname_in_settings(key='k', settings=settings)
    def f():
        return ''

    f()
    assert settings.value('k') == '/old/dir'
