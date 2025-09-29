import os, sys, time, re, subprocess, importlib.util, pathlib, multiprocessing as mp
import cv2

import subprocess, sys, re
import winreg

_BLACKLIST = re.compile(r"(OBS|Virtual|DroidCam|ManyCam|Snap)", re.I)

def _ps_path():
    # 확실한 절대경로(환경 변수 오염 회피)
    return r"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

def _enum_ps():
    try:
        ps = r"Get-CimInstance Win32_PnPEntity | ?{ $_.PNPClass -in @('Image','Camera') } | Select-Object -ExpandProperty Name"
        r = subprocess.run([_ps_path(), "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, text=True, timeout=2)
        names = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        return [n for n in names if not _BLACKLIST.search(n)]
    except Exception:
        return []

def _enum_wmic():
    try:
        # WMIC는 deprecated지만 현장에서 막힐 가능성이 낮음
        r = subprocess.run(["wmic", "path", "win32_pnpentity", "where",
                            "(PNPClass='Image' or PNPClass='Camera')", "get", "Name"],
                           capture_output=True, text=True, timeout=2)
        names = [ln.strip() for ln in r.stdout.splitlines() if ln.strip() and ln.strip() != "Name"]
        return [n for n in names if not _BLACKLIST.search(n)]
    except Exception:
        return []

def _enum_registry():
    # HKLM\SYSTEM\CurrentControlSet\Enum\* 트리에서 FriendlyName/DeviceDesc을 긁음
    results = []
    try:
        hive = winreg.HKEY_LOCAL_MACHINE
        base = r"SYSTEM\CurrentControlSet\Enum"
        def walk(key):
            try:
                with winreg.OpenKey(hive, key) as k:
                    # 하위 키 순회
                    i = 0
                    while True:
                        try:
                            sub = winreg.EnumKey(k, i); i += 1
                        except OSError:
                            break
                        walk(f"{key}\\{sub}")
                    # 값 읽기
                    try:
                        cls, _ = winreg.QueryValueEx(k, "Class")         # "Image" / "Camera" 등
                    except OSError:
                        cls = None
                    if cls not in ("Image", "Camera"):
                        return
                    name = None
                    for valname in ("FriendlyName", "DeviceDesc"):
                        try:
                            v, _ = winreg.QueryValueEx(k, valname)
                            if isinstance(v, str) and v.strip():
                                name = v.strip(); break
                        except OSError:
                            pass
                    if name and not _BLACKLIST.search(name):
                        results.append(name)
            except OSError:
                pass
        walk(base)
    except Exception:
        return []
    # 중복 제거(순서 유지)
    seen, out = set(), []
    for n in results:
        if n not in seen:
            seen.add(n); out.append(n)
    return out

def enum_camera_names():
    for fn in (_enum_ps, _enum_wmic, _enum_registry):
        names = fn()
        if names:
            return names
    return []

    
print("Enumerating camera names...")
print(enum_camera_names())