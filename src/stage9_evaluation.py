from pathlib import Path
import csv
import json
import hashlib

from stage7_dataset_test import analyze_mesh


def load_manifest(
    dataset_dir:Path
)->dict[str,dict]:
    manifest_path:Path=dataset_dir/"manifest.json"
    if not manifest_path.exists():
        return {}

    with manifest_path.open("r",encoding="utf-8") as file:
        manifest:dict=json.load(file)

    result:dict[str,dict]={}
    for case in manifest["cases"]:
        result[case["name"]]=case

    return result


def geometry_hash(
    mesh_path:Path
)->str:
    data:bytes=mesh_path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def evaluate_case(
    mesh_path:Path,
    manifest:dict[str,dict]
)->dict:
    result:dict=analyze_mesh(mesh_path)

    case_info:dict=manifest.get(
        mesh_path.stem,
        {}
    )

    result["semantic_label"]=case_info.get(
        "semantic_label",
        "unknown"
    )

    result["shape_family"]=case_info.get(
        "shape_family",
        "unknown"
    )

    result["geometry_hash"]=geometry_hash(
        mesh_path
    )

    result["automatic_repair"]=(
        result.get("s8_safe") is True
        and result.get("s8_valid") is True
    )

    return result


def regression_checks(
    results:list[dict]
)->list[dict]:
    checks:list[dict]=[]
    by_name:dict[str,dict]={
        result["mesh"]:result
        for result in results
    }

    def add_check(
        name:str,
        passed:bool
    )->None:
        checks.append({
            "name":name,
            "passed":passed
        })

    if "baseline_cube" in by_name:
        add_check(
            "baseline_cube_is_keep",
            by_name["baseline_cube"]["decision"]=="keep"
        )

    if "appendage_long" in by_name:
        result:dict=by_name["appendage_long"]
        add_check(
            "appendage_long_safe_repair",
            result.get("s8_safe") is True
            and result.get("s8_valid") is True
        )

    if "appendage_medium" in by_name:
        result:dict=by_name["appendage_medium"]
        add_check(
            "appendage_medium_safe_refusal",
            result.get("s8_safe") is False
            and "boundary_not_planar"
            in result.get("s8_safety_reason",[])
        )

    if "legitimate_compact_boss" in by_name:
        add_check(
            "compact_boss_is_keep",
            by_name["legitimate_compact_boss"]["decision"]=="keep"
        )

    groups:dict[str,list[dict]]={}
    for result in results:
        h:str=result["geometry_hash"]
        if h not in groups:
            groups[h]=[]
        groups[h].append(result)

    for group in groups.values():
        if len(group)<2:
            continue

        reference:dict=group[0]
        consistent:bool=True

        for result in group[1:]:
            if (
                result["decision"]!=reference["decision"]
                or result.get("s8_safe")!=reference.get("s8_safe")
                or result.get("s8_valid")!=reference.get("s8_valid")
            ):
                consistent=False

        names:str=",".join(
            result["mesh"]
            for result in group
        )

        add_check(
            f"duplicate_geometry_consistency:{names}",
            consistent
        )

    return checks


def print_summary(
    results:list[dict],
    checks:list[dict]
)->None:
    total:int=len(results)

    keep:int=sum(
        result["decision"]=="keep"
        for result in results
    )

    manual:int=sum(
        result["decision"]=="manual_review"
        for result in results
    )

    candidates:list[dict]=[
        result for result in results
        if result["decision"]=="repair_candidate"
    ]

    safe:list[dict]=[
        result for result in candidates
        if result.get("s8_safe") is True
    ]

    refused:list[dict]=[
        result for result in candidates
        if result.get("s8_safe") is False
    ]

    valid_repairs:list[dict]=[
        result for result in safe
        if result.get("s8_valid") is True
    ]

    invalid_repairs:list[dict]=[
        result for result in safe
        if result.get("s8_valid") is False
    ]

    legitimate_auto:list[dict]=[
        result for result in valid_repairs
        if result["semantic_label"]=="legitimate"
    ]

    defect_auto:list[dict]=[
        result for result in valid_repairs
        if result["semantic_label"]=="defect_like"
    ]

    unique_geometry:int=len({
        result["geometry_hash"]
        for result in results
    })

    print()
    print("="*70)
    print("S9 EVALUATION SUMMARY")
    print("="*70)

    print("Total cases:",total)
    print("Unique geometries:",unique_geometry)
    print()

    print("S7:")
    print(" keep:",keep)
    print(" manual_review:",manual)
    print(" repair_candidate:",len(candidates))
    print()

    print("S8:")
    print(" safety passed:",len(safe))
    print(" safety refused:",len(refused))
    print(" valid repairs:",len(valid_repairs))
    print(" invalid repairs:",len(invalid_repairs))

    if len(candidates)>0:
        print(
            " safety coverage:",
            f"{len(safe)/len(candidates):.3f}"
        )

    if len(safe)>0:
        print(
            " geometric repair success:",
            f"{len(valid_repairs)/len(safe):.3f}"
        )

    print()
    print("Semantic audit:")
    print(
        " legitimate meshes automatically repaired:",
        len(legitimate_auto)
    )
    print(
        " defect-like meshes automatically repaired:",
        len(defect_auto)
    )

    if len(valid_repairs)>0:
        print(
            " semantic false-repair fraction:",
            f"{len(legitimate_auto)/len(valid_repairs):.3f}"
        )

    print()
    print("Regression checks:")

    for check in checks:
        status:str="PASS" if check["passed"] else "FAIL"
        print(
            f" {status:<4}  {check['name']}"
        )

    print("="*70)


def write_csv(
    results:list[dict],
    output_path:Path
)->None:
    fields:list[str]=[
        "mesh",
        "semantic_label",
        "shape_family",
        "decision",
        "shape_class",
        "candidate_fraction",
        "conductance",
        "fiedler_eigengap",
        "s8_safe",
        "s8_valid",
        "automatic_repair",
        "s8_safety_reason",
        "s8_validation_reason",
        "geometry_hash"
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer=csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for result in results:
            row:dict={}

            for field in fields:
                value=result.get(field)

                if isinstance(value,list):
                    value="|".join(value)

                row[field]=value

            writer.writerow(row)


def main()->None:
    project_root:Path=(
        Path(__file__)
        .resolve()
        .parents[1]
    )

    dataset_dir:Path=(
        project_root
        /"data"
        /"raw_meshes"
        /"synthetic_s7"
    )

    manifest:dict[str,dict]=load_manifest(
        dataset_dir
    )

    mesh_paths:list[Path]=sorted(
        dataset_dir.glob("*.obj")
    )

    if len(mesh_paths)==0:
        raise RuntimeError(
            f"No OBJ files found in {dataset_dir}"
        )

    results:list[dict]=[]

    for mesh_path in mesh_paths:
        print(
            f"Evaluating: {mesh_path.name}"
        )

        result:dict=evaluate_case(
            mesh_path,
            manifest
        )

        results.append(result)

    checks:list[dict]=regression_checks(
        results
    )

    print_summary(
        results,
        checks
    )

    output_path:Path=(
        dataset_dir
        /"stage9_results.csv"
    )

    write_csv(
        results,
        output_path
    )

    print(
        "Saved:",
        output_path
    )


if __name__=="__main__":
    main()