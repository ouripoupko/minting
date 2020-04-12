
from settings import Settings
from everyone import Everyone

if __name__ == "__main__":
    settings = Settings()
    everyone = Everyone(settings)
    everyone.start()

