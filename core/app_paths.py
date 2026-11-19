import os
import shutil
import sys
from pathlib import Path


APP_DATA_NAME = "ConfigGenerator"
MIGRATION_MARKER = ".legacy-data-migrated"


def resource_path(relative_path: str) -> Path:
    bundle_dir = getattr(sys, "_MEIPASS", None)
    base_dir = Path(bundle_dir) if bundle_dir else Path(__file__).resolve().parent.parent
    return base_dir / relative_path


def _legacy_data_roots() -> list[Path]:
    if not getattr(sys, "frozen", False):
        return [Path(__file__).resolve().parent.parent]

    candidates = [Path.cwd()]
    executable = Path(sys.executable).resolve()
    if len(executable.parents) > 2:
        candidates.append(executable.parents[2])

    roots = []
    seen = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate not in seen and (candidate / "ConfigGenerator.spec").is_file():
            roots.append(candidate)
            seen.add(candidate)
    return roots


def _migrate_legacy_data(data_dir: Path, legacy_roots: list[Path]) -> None:
    marker = data_dir / MIGRATION_MARKER
    if marker.exists():
        return

    for legacy_root in legacy_roots:
        legacy_root = Path(legacy_root).resolve()
        if legacy_root == data_dir.resolve():
            continue

        old_config = legacy_root / "config.json"
        new_config = data_dir / "config.json"
        if old_config.is_file() and not new_config.exists():
            shutil.copy2(old_config, new_config)

        old_profiles = legacy_root / "profiles"
        if old_profiles.is_dir():
            new_profiles = data_dir / "profiles"
            new_profiles.mkdir(parents=True, exist_ok=True)
            for old_profile in old_profiles.glob("*.json"):
                new_profile = new_profiles / old_profile.name
                if not new_profile.exists():
                    shutil.copy2(old_profile, new_profile)

    marker.touch()


def user_data_dir(
    base_dir: str | Path | None = None,
    legacy_roots: list[Path] | None = None
) -> Path:
    if base_dir is None:
        roaming_dir = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        data_dir = roaming_dir / APP_DATA_NAME
    else:
        data_dir = Path(base_dir)

    if legacy_roots is None:
        legacy_roots = _legacy_data_roots() if base_dir is None else []

    data_dir.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_data(data_dir, legacy_roots)
    return data_dir
