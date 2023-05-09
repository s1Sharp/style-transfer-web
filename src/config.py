import os
from dotenv import load_dotenv


class WebEnvControl():

    def __init__(self, config_file_path) -> None:

        load_env_result = load_dotenv(dotenv_path=config_file_path, override=True, verbose=True)
        print("load env ok" if load_env_result else "load env fail")

        self.PROJECT_ROOT = os.environ.get("PROJECT_ROOT", "")
        self.GPU = False if os.environ.get("GPU", 'False') == 'False' else True
        self.POSTGRE_URL = os.environ.get("POSTGRE_URL", "")
        self.POSTGRE_URL_TEST = os.environ.get("POSTGRE_URL_TEST", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
        self.SECRET_AUTH = os.environ.get("SECRET_AUTH", "")
        self.S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "")
        self.S3_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID", "")
        self.S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY", "")
        self.REDIS_URL = os.environ.get("REDIS_URL", "")
        self.DOMEN_URL = os.environ.get("DOMEN_URL", "")


PROJECT_ROOT = os.environ.get("PROJECT_ROOT")
if PROJECT_ROOT is None:
    raise FileNotFoundError("PROJECT_ROOT")

path=f'{PROJECT_ROOT}/config/.env_release'

env_control = WebEnvControl(path)

SECRET_AUTH = env_control.SECRET_AUTH
POSTGRE_URL = env_control.POSTGRE_URL
POSTGRE_URL_TEST = env_control.POSTGRE_URL_TEST
REDIS_URL = env_control.REDIS_URL
DOMEN_URL = env_control.DOMEN_URL