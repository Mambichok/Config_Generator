import os
import winreg
from pathlib import Path
from models.profile import Profile, AppItem


class BatGenerator:
    def __init__(self, desktop_path=None):
        if desktop_path:
            self.desktop = Path(desktop_path)
        else:
            self.desktop = Path(self._get_real_desktop_path())
    
    def _get_real_desktop_path(self) -> str:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
            winreg.CloseKey(key)
            desktop_path = os.path.expandvars(desktop_path)
            if Path(desktop_path).exists():
                return desktop_path
        except Exception:
            pass
        
        # Fallback to OneDrive paths
        onedrive_paths = [
            Path.home() / "OneDrive" / "Desktop",
            Path.home() / "OneDrive" / "Рабочий стол",
        ]
        for path in onedrive_paths:
            if path.exists():
                return str(path)
        
        return str(Path.home() / "Desktop")
    
    def generate(self, profile: Profile) -> Path:
        bat_path = self.desktop / f"{profile.filename}.bat"
        
        lines = [
            "@echo off",
            "chcp 65001 >nul",
        ]

        if profile.run_as_admin:
            lines.extend([
                "fltmc >nul 2>&1",
                "if errorlevel 1 (",
                '    set "CONFIG_GENERATOR_BAT=%~f0"',
                '    powershell -NoProfile -Command "Start-Process -FilePath $env:ComSpec -ArgumentList (\'/c \' + [char]34 + $env:CONFIG_GENERATOR_BAT + [char]34) -Verb RunAs"',
                "    exit /b",
                ")",
            ])

        lines.extend([
            f"title {profile.name}",
            f"echo Launching: {profile.name}",
            "echo ---------------------------",
            "",
        ])
        
        for item in profile.items:
            lines.extend(self._process_item(item, profile))
            if profile.delay > 0:
                lines.append(f"timeout /t {profile.delay} /nobreak >nul")
            lines.append("")
        
        lines.extend([
            "echo ---------------------------",
            "echo All apps launched!",
            "pause",
        ])
        
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        return bat_path
    
    def _process_item(self, item: AppItem, profile: Profile) -> list:
        lines = []
        app_name = Path(item.path).name
        
        lines.append(f'tasklist /FI "IMAGENAME eq {app_name}" 2>nul | find /I "{app_name}" >nul')
        lines.append(f'if %errorlevel% equ 0 (')
        lines.append(f'    echo [SKIP] {item.name} already running')
        lines.append(f') else (')
        
        if item.is_browser and item.urls:
            if profile.single_browser_window:
                urls = " ".join(f'"{url}"' for url in item.urls)
                cmd = f'    start "" "{item.path}" {urls}'
            else:
                cmd = f'    start "" "{item.path}"'
                for url in item.urls:
                    cmd += f' "{url}"'
            lines.append(cmd)
        else:
            cmd = f'    start "" "{item.path}"'
            if item.args:
                cmd += f" {item.args}"
            lines.append(cmd)
        
        lines.append(f'    echo [OK] {item.name} launched')
        lines.append(f')')
        
        return lines