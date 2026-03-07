from dotenv import load_dotenv

load_dotenv()

pytest_plugins = [
    "fixtures.api_fixtures",
    "fixtures.db_fixtures"
]