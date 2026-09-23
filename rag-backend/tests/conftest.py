from app.db.database import init_db


def pytest_sessionstart(session):
    init_db()
