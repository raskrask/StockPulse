from infrastructure.persistence.screening_profile import ScreeningProfile

class ScreeningProfileUsecase:
    def __init__(self):
        self.repo = ScreeningProfile()

    def list_profiles(self):
        return self.repo.list_profiles()

    def load_profile(self, name: str) -> dict:
        return self.repo.load(name)

    def save_profile(self, name: str, data: dict):
        self.repo.save(name, data)
        return True