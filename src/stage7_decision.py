def ambiguity_judge(candidate_fraction:float,shape:str,eigengap:float,)->list[str]:
    result:list[str]=[]
    t_localized: float = 0.35
    t_global: float = 0.45
    t_eigengap:float = 0.001
    if candidate_fraction > t_localized and candidate_fraction<t_global:
        result.append("borderline_localization")
    if shape == "intermediate":
        result.append("geometry_ambiguity")
    if eigengap < t_eigengap:
        result.append("spectral_instability")
    return result
def classify_shape(
    ratio_2: float,
    ratio_3: float
) -> str:
    t_low=0.08
    t_high=0.5
    if ratio_2<t_low and ratio_3<t_low:
        return "rod"
    if ratio_2>t_high and ratio_3>t_high:
        return "compact"
    if ratio_2>t_high and ratio_3<t_low:
        return "sheet"
    return "intermediate"
def classify_stage7(
        spectral_result:dict,
        geometry_result:dict,
        candidate_fraction:float
)->dict:
    pvr1,pvr2=geometry_result["principal_variance_ratios"]
    shape:str=classify_shape(float(pvr1),float(pvr2))
    eigengap:float|None=spectral_result["fiedler_eigengap"]
    t_global: float = 0.45
    reason_codes: list[str] = []
    if candidate_fraction >= t_global:
        decision: str = "keep"
        reason_codes.append("global_body_split")
        return {
            "decision": decision,
            "reason_codes": reason_codes,
            "shape_class": shape,
            "ambiguity_flags": []
        }
    if eigengap is None:
        return {
            "decision": "manual_review",
            "reason_codes": ["insufficient_spectral_evidence"],
            "shape_class": shape,
            "ambiguity_flags": ["spectral_instability"]
        }
    ambiguity_flags:list[str]=ambiguity_judge(candidate_fraction,shape,eigengap)
    conductance: float = spectral_result["best_conductance"]
    t_conductance: float = 0.03

    if len(ambiguity_flags) > 0:
        decision = "manual_review"
        reason_codes.append("ambiguous_evidence")

    elif conductance <= t_conductance:
        decision = "repair_candidate"
        reason_codes.append("localized_attachment")
        reason_codes.append("strong_bottleneck")
        reason_codes.append(f"{shape}_geometry")

    else:
        decision = "manual_review"
        reason_codes.append("localized_attachment")
        reason_codes.append("weak_bottleneck_evidence")
    return {
        "decision": decision,
        "reason_codes": reason_codes,
        "shape_class": shape,
        "ambiguity_flags": ambiguity_flags,
    }
