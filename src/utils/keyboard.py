import subprocess, os, shutil

TABTIP_DEFAULT = r"C:\Program Files\Common Files\Microsoft Shared\ink\TabTip.exe"
OSK_DEFAULT = r"C:\Windows\System32\osk.exe"

def find_touch_keyboard():
    # 우선 TabTip(터치 키보드) 우선, 없으면 OSK(화면 키보드)로 폴백
    if os.path.exists(TABTIP_DEFAULT):
        return TABTIP_DEFAULT
    tabtip = shutil.which("TabTip.exe")
    if tabtip:
        return tabtip
    if os.path.exists(OSK_DEFAULT):
        return OSK_DEFAULT
    osk = shutil.which("osk.exe")
    return osk  # 없으면 None

KB_PATH = find_touch_keyboard()

def show_touch_keyboard():
    if KB_PATH is None:
        return
    # 이미 떠 있으면 재실행해도 포커싱만 됩니다.
    try:
        subprocess.Popen([KB_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def hide_touch_keyboard():
    # TabTip은 종료 대신 숨김만 될 때가 있어 taskkill을 사용 (필요 시 주석 처리)
    try:
        subprocess.run(["taskkill", "/IM", "TabTip.exe", "/F"], capture_output=True)
    except Exception:
        pass
    # OSK도 함께 종료 시도
    try:
        subprocess.run(["taskkill", "/IM", "osk.exe", "/F"], capture_output=True)
    except Exception:
        pass

