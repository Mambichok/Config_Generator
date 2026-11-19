import json
from pathlib import Path
from core.app_paths import user_data_dir
from models.profile import Profile


class ProfileManager:
    def __init__(self, profiles_dir=None):
        self.profiles_dir = (
            Path(profiles_dir)
            if profiles_dir is not None
            else user_data_dir() / "profiles"
        )
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    def save_profile(self, profile: Profile):
        filepath = self.profiles_dir / f"{profile.filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
    
    def load_profile(self, filename: str) -> Profile:
        filepath = self.profiles_dir / f"{filename}.json"
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Profile.from_dict(data)
    
    def list_profiles(self) -> list:
        return [f.stem for f in self.profiles_dir.glob("*.json")]
    
    def delete_profile(self, filename: str):
        filepath = self.profiles_dir / f"{filename}.json"
        if filepath.exists():
            filepath.unlink()