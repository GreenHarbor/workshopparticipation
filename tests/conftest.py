import pytest


@pytest.fixture
def client():
    from src import app

    app.app.config['TESTING'] = True

    return app.app.test_client()

def pytest_runtest_logreport(report):
    report.nodeid = "..." + report.nodeid[-10:]