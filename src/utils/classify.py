THRESH = dict(
    INV_TRIANGLE=1.12,   # S/H, S/W (Y형)
    PEAR=1.12,           # H/S (A형)
    HOURGLASS_WAIST=0.78,
    O_ABDOMEN=1.10,      # A / max(S,H)
    O_WAIST_MALE=1.4,   # W / mean(S,H)
    O_WAIST_FEMALE=1.3
)

def classify_body_shape(gender, S, H, W, A):
    eps = 1e-6
    if min(S, H, W) < eps:
        return "UNKNOWN"
    meanSH = (S + H) / 2.0
    shoulder_hip = S / (H + eps)
    hip_shoulder = H / (S + eps)
    waist_mean = W / (meanSH + eps)
    abdomen_max = A / max(S, H, eps)
    o_waist_thr = THRESH['O_WAIST_MALE'] if gender == 'male' else THRESH['O_WAIST_FEMALE']
    if abdomen_max >= THRESH['O_ABDOMEN'] and waist_mean >= o_waist_thr:
        return "O"
    if shoulder_hip >= THRESH['INV_TRIANGLE'] and (S / (W + eps)) >= THRESH['INV_TRIANGLE']:
        return "Y"
    if gender == 'female':
        if hip_shoulder >= THRESH['PEAR'] and (W / (H + eps)) <= 0.85:
            return "A"
        if abs(shoulder_hip - 1.0) <= 0.08 and waist_mean <= THRESH['HOURGLASS_WAIST']:
            return "X"
    return "H"
