import cv2
import numpy as np
import mediapipe as mp

def draw_pose_letter(image, letter, color=(0, 255, 0), thickness=None, vis_thresh=0.5):
    """
    MediaPipe Pose를 사용하여 인체(어깨/골반) 기준으로 알파벳 X, O, A, Y, H를
    '정확한 글자 형태'로 그려 반환합니다.

    Parameters
    ----------
    image : np.ndarray(BGR) 또는 str
        BGR 배열(cv2.imread 결과) 또는 이미지 파일 경로.
    letter : {'X','O','A','Y','H'}
    color : BGR 튜플
    thickness : int or None
        None이면 이미지 크기에 비례해 자동 설정.
    vis_thresh : float
        랜드마크 가시성 임계치(기본 0.5)

    Returns
    -------
    out_img : np.ndarray (BGR)

    Raises
    ------
    ValueError : 포즈 미검출/불충분 또는 유효하지 않은 letter
    """

    # ----- 입력 처리 -----
    if isinstance(image, str):
        img = cv2.imread(image)
        if img is None:
            raise ValueError("이미지 경로를 읽을 수 없습니다.")
    elif isinstance(image, np.ndarray):
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("image는 BGR 3채널 np.ndarray 여야 합니다.")
        img = image.copy()
    else:
        raise ValueError("image는 파일 경로(str) 또는 BGR np.ndarray여야 합니다.")

    h, w = img.shape[:2]
    if thickness is None:
        thickness = max(2, int(round(min(h, w) * 0.006)))

    # ----- MediaPipe Pose -----
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True,
                      model_complexity=1,
                      enable_segmentation=False,
                      min_detection_confidence=0.5) as pose:
        res = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    if not res.pose_landmarks:
        raise ValueError("포즈를 검출하지 못했습니다.")

    lm = res.pose_landmarks.landmark

    # 필요한 포인트 인덱스
    L_SHOULDER, R_SHOULDER = 11, 12
    L_HIP, R_HIP = 23, 24

    need = [L_SHOULDER, R_SHOULDER, L_HIP, R_HIP]
    for i in need:
        if lm[i].visibility < vis_thresh:
            raise ValueError("필요한 관절(어깨/골반)의 가시성이 낮습니다.")

    def px(i):
        return np.array([lm[i].x * w, lm[i].y * h], dtype=np.float32)

    p_ls = px(L_SHOULDER)
    p_rs = px(R_SHOULDER)
    p_lh = px(L_HIP)
    p_rh = px(R_HIP)

    # 파생점
    p_sh_mid = 0.5 * (p_ls + p_rs)   # 어깨 중앙
    p_hp_mid = 0.5 * (p_lh + p_rh)   # 골반 중앙
    p_mid    = 0.5 * (p_sh_mid + p_hp_mid)  # 어깨-골반 중간

    def P(pt):
        return (int(round(float(pt[0]))), int(round(float(pt[1]))))

    def draw_seg(a, b):
        cv2.line(img, P(a), P(b), color, thickness, cv2.LINE_AA)

    # 수평선과 선분 교점 (A/H 횡선에 사용)
    def intersect_horizontal(p1, p2, y):
        y1, y2 = p1[1], p2[1]
        if abs(y2 - y1) < 1e-6:
            return None, None
        t = (y - y1) / (y2 - y1)
        x = p1[0] + t * (p2[0] - p1[0])
        return np.array([x, y], dtype=np.float32), t

    # ----- O 전용: 4점 정확 통과 + 알파벳형 O (원호 기반 베지어) -----
    def draw_O_from_four_points(points, samples_per_quarter=30):
        # 1) 중심: 대각선 교점
        def line_intersect(p1, p2, q1, q2):
            # p1 + t*(p2-p1) = q1 + u*(q2-q1)
            r = p2 - p1
            s = q2 - q1
            denom = r[0]*s[1] - r[1]*s[0]
            if abs(denom) < 1e-8:
                return None
            t = ((q1[0]-p1[0])*s[1] - (q1[1]-p1[1])*s[0]) / denom
            return p1 + t*r

        c = line_intersect(points[0], points[2], points[1], points[3])
        if c is None:
            c = 0.5 * (p_sh_mid + p_hp_mid)  # 보정(평행에 가까운 경우)

        # 2) 각도 기준으로 CCW 정렬
        def ang(p):
            v = p - c
            return np.arctan2(v[1], v[0])
        pts = sorted(points, key=ang)
        angs = [ang(p) for p in pts]

        # 3) 보조: 90° CCW 회전
        def rot90_ccw(v):
            return np.array([-v[1], v[0]], dtype=np.float32)

        # 4) 각 세그먼트에 대해 베지어 구성 (원호 근사)
        curve = []
        for i in range(4):
            p0 = pts[i]
            p1 = pts[(i+1) % 4]
            a0 = angs[i]
            a1 = angs[(i+1) % 4]

            dth = a1 - a0
            if dth <= 0:
                dth += 2*np.pi

            v0 = p0 - c; r0 = np.linalg.norm(v0) + 1e-8
            v1 = p1 - c; r1 = np.linalg.norm(v1) + 1e-8

            t0_dir = rot90_ccw(v0 / r0)   # 접선 방향(단위)
            t1_dir = rot90_ccw(v1 / r1)

            # 원호의 베지어 핸들 길이: h = (4/3) * tan(Δθ/4) * r
            k = (4.0/3.0) * np.tan(dth / 4.0)
            h0 = k * r0
            h1 = k * r1

            c1 = p0 + t0_dir * h0
            c2 = p1 - t1_dir * h1

            # 베지어 샘플링
            n = max(12, int(round(samples_per_quarter * dth / (np.pi/2))))
            t_vals = np.linspace(0, 1, n, endpoint=False) if i < 3 else np.linspace(0, 1, n, endpoint=True)
            for t in t_vals:
                # Cubic Bezier: B(t) = (1-t)^3 P0 + 3(1-t)^2 t C1 + 3(1-t) t^2 C2 + t^3 P1
                mt = 1 - t
                pt = (mt**3)*p0 + 3*(mt**2)*t*c1 + 3*mt*(t**2)*c2 + (t**3)*p1
                curve.append(P(pt))

        cv2.polylines(img, [np.array(curve, dtype=np.int32)], isClosed=True,
                      color=color, thickness=thickness, lineType=cv2.LINE_AA)

    L = letter.upper()

    if L == 'X':
        # 대각선 두 줄로 정확한 X
        draw_seg(p_ls, p_rh)
        draw_seg(p_rs, p_lh)

    elif L == 'O':
        # 네 점을 '정확히 통과'하면서 'O답게' 부드러운 폐곡선을 생성
        draw_O_from_four_points([p_ls, p_rs, p_rh, p_lh])

    elif L == 'A':
        # 다리(직선) 두 개: 꼭짓점=어깨 중앙
        draw_seg(p_sh_mid, p_lh)
        draw_seg(p_sh_mid, p_rh)
        # 횡선: 어깨-골반 중간 높이의 수평선이 두 다리와 만나는 점들을 잇기
        y_cross = float(p_mid[1])
        left_x, tL  = intersect_horizontal(p_sh_mid, p_lh, y_cross)
        right_x, tR = intersect_horizontal(p_sh_mid, p_rh, y_cross)
        if left_x is not None and right_x is not None and 0.0 <= (tL or 0) <= 1.0 and 0.0 <= (tR or 0) <= 1.0:
            draw_seg(left_x, right_x)

    elif L == 'Y':
        # 분기점: 어깨→골반을 1:2로 나눈 지점(어깨 쪽이 더 가깝게) -> 글자 비례 안정
        junction = p_sh_mid * (2/3) + p_hp_mid * (1/3)
        draw_seg(p_ls, junction)   # 양팔
        draw_seg(p_rs, junction)
        draw_seg(junction, p_hp_mid)  # 기둥

    elif L == 'H':
        # 세로 기둥 두 개
        draw_seg(p_ls, p_lh)
        draw_seg(p_rs, p_rh)
        # 중앙 횡선(수평): 어깨-골반 중간 높이
        y_cross = float(p_mid[1])
        left_cross, _  = intersect_horizontal(p_ls, p_lh, y_cross)
        right_cross, _ = intersect_horizontal(p_rs, p_rh, y_cross)
        if left_cross is not None and right_cross is not None:
            draw_seg(left_cross, right_cross)

    else:
        raise ValueError("letter는 'X','O','A','Y','H' 중 하나여야 합니다.")

    return img
