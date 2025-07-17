import json
import sys
from pathlib import Path

def load_persona(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compare_big_five(a: dict, b: dict) -> dict:
    keys = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    diffs = {}
    for k in keys:
        diffs[k] = round(abs(a.get(k, 0) - b.get(k, 0)), 2)
    return diffs

def print_comparison(persona_a, persona_b, name_a, name_b):
    print(f"\n📊 Comparing {name_a} vs {name_b}\n")

    mbti_a = persona_a.get("personality_frameworks", {}).get("MBTI", "Unknown")
    mbti_b = persona_b.get("personality_frameworks", {}).get("MBTI", "Unknown")
    print(f"MBTI: {name_a}: {mbti_a} | {name_b}: {mbti_b}\n")

    big5_a = persona_a.get("personality_frameworks", {}).get("BigFive", {})
    big5_b = persona_b.get("personality_frameworks", {}).get("BigFive", {})
    big5_diff = compare_big_five(big5_a, big5_b)

    print("🧠 Big Five Trait Comparison (Absolute Difference)")
    for trait, diff in big5_diff.items():
        print(f"  {trait.title():<15}: Δ {diff:.2f}  | {name_a}: {big5_a.get(trait, '-'):.2f}  | {name_b}: {big5_b.get(trait, '-'):.2f}")

    print("\n🎯 Section Confidence Comparison")
    keys = ["interests", "personality_traits", "tone_of_writing", "goals_and_needs"]
    for key in keys:
        conf_a = persona_a.get(key, {}).get("confidence", 0)
        conf_b = persona_b.get(key, {}).get("confidence", 0)
        print(f"  {key.replace('_', ' ').title():<25}: {name_a}: {conf_a:.2f} | {name_b}: {conf_b:.2f}")
    print("\n📄 Full Persona Text Comparison")
    export_comparison_to_md(persona_a, persona_b, name_a, name_b, keys)
    # print("--------------------------------------------------")

    # for key in keys:
    #     print(f"\n🔹 {key.replace('_', ' ').title()}")
    #     print(f"{name_a}:")
    #     print(persona_a.get(key, {}).get("value", "[No data]").strip())
    #     print()
    #     print(f"{name_b}:")
    #     print(persona_b.get(key, {}).get("value", "[No data]").strip())
    #     print("-" * 50)

def export_comparison_to_md(persona_a, persona_b, name_a, name_b, keys):
    filename = f"{name_a}_vs_{name_b}_comparison.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Persona Comparison: {name_a} vs {name_b}\n\n")

        f.write(f"**MBTI**\n\n{name_a}: `{persona_a.get('personality_frameworks', {}).get('MBTI', 'Unknown')}`\n\n")
        f.write(f"{name_b}: `{persona_b.get('personality_frameworks', {}).get('MBTI', 'Unknown')}`\n\n")

        f.write(f"## Big Five Trait Comparison\n\n")
        big5_diff = compare_big_five(
            persona_a.get("personality_frameworks", {}).get("BigFive", {}),
            persona_b.get("personality_frameworks", {}).get("BigFive", {})
        )
        for trait, diff in big5_diff.items():
            f.write(f"- **{trait.title()}**: Δ {diff:.2f}\n")

        f.write("\n## Section Confidence Comparison\n")
        for key in keys:
            conf_a = persona_a.get(key, {}).get("confidence", 0)
            conf_b = persona_b.get(key, {}).get("confidence", 0)
            f.write(f"- **{key.replace('_', ' ').title()}**: {name_a}: {conf_a:.2f}, {name_b}: {conf_b:.2f}\n")

        f.write("\n## Full Persona Text Comparison\n")
        for key in keys:
            f.write(f"\n### {key.replace('_', ' ').title()}\n")
            f.write(f"**{name_a}:**\n\n{persona_a.get(key, {}).get('value', '').strip()}\n\n")
            f.write(f"**{name_b}:**\n\n{persona_b.get(key, {}).get('value', '').strip()}\n\n")

    print(f"\n📝 Comparison saved to `{filename}`")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        file_a, file_b = sys.argv[1], sys.argv[2]
    else:
        print("📥 No files provided as arguments.")
        file_a = input("Enter path to first persona JSON file: ").strip()
        file_b = input("Enter path to second persona JSON file: ").strip()
        # print(f"📥 Comparing {file_a} vs {file_b}\n")
    if not Path(file_a).is_file() or not Path(file_b).is_file():
        print("❌ One or both files do not exist. Please check the paths.")
        sys.exit(1)

    name_a = Path(file_a).stem.replace("_persona", "")
    name_b = Path(file_b).stem.replace("_persona", "")
    print(f"📊 Comparing personas: {name_a} vs {name_b}\n")
    persona_a = load_persona(file_a)
    persona_b = load_persona(file_b)

    print_comparison(persona_a, persona_b, name_a, name_b)
    print("\n📄 Full Persona Text Comparison")
    
