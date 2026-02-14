def age_group(age):
    if age < 40:
        return 0
    elif age < 60:
        return 1
    else:
        return 2


def compute_vital_score(bp, hr, temp):
    score = 0
    
    if bp > 180 or bp < 90:
        score += 3
    elif bp > 150:
        score += 2
    elif bp > 130:
        score += 1
        
    if hr > 130 or hr < 40:
        score += 3
    elif hr > 110:
        score += 2
    elif hr > 100:
        score += 1
        
    if temp > 39.5:
        score += 3
    elif temp > 38.5:
        score += 2
    elif temp > 37.5:
        score += 1
        
    return score
