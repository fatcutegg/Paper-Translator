#!/usr/bin/env python3
import os
import re
import sys

def verify_skill_md(file_path="SKILL.md"):
    """
    方案 C: 静的チェッカー (SKILL.md自体のゴミや构文エラーを验证)
    """
    print(f"[*] Verifying {file_path}...")
    if not os.path.exists(file_path):
        print(f"[ERROR] {file_path} does not exist.")
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 检测语言上的垃圾模式 (中文中无意中混入的英文・日文等)
    glitches = [
        (r"(?<![a-zA-Z])of(?![a-zA-Z])", "English 'of' inside Chinese text (should be '的')"),
        (r"(?<![a-zA-Z])and(?![a-zA-Z])", "English 'and' inside Chinese text (should be '与' or '或')"),
        (r"(?<![a-zA-Z])any(?![a-zA-Z])", "English 'any' inside Chinese text (should be '任何')"),
        (r"の", "Japanese 'の' inside Chinese text"),
        (r"集", "Duplicate '集的的'")
    ]
    
    success = True
    lines = content.split("\n")
    
    in_code_block = False
    
    for line_idx, line in enumerate(lines):
        line_no = line_idx + 1
        
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            continue
            
        for pattern, desc in glitches:
            matches = list(re.finditer(pattern, line, re.IGNORECASE))
            for m in matches:
                if any(x in line for x in ["English", "Environment", "Strict", "Self-Check", "Original", "Style", "Goal"]):
                    continue
                print(f"[WARN] {desc} at line {line_no}:")
                print(f"  -> {line.strip()}")
                success = False
                
    if success:
        print("[SUCCESS] SKILL.md verification passed.")
    else:
        print("[FAILED] SKILL.md verification failed with potential translation glitches.")
    return success


def verify_vault_structure(vault_path="."):
    """
    方案 A: 生成物整合性チェッカー (My_Research_Vaultの链接切れや画像・Mermaidの构文エラーを验证)
    """
    print(f"[*] Verifying Vault structure in '{vault_path}'...")
    
    required_files = [
        "INDEX_论文阅读总目录.md",
        "01_Sources/INDEX_独立目录.md",
        "02_Brain/INDEX_全局术语汇总.md"
    ]
    
    all_exist = True
    for f in required_files:
        path = os.path.join(vault_path, f)
        if not os.path.exists(path):
            print(f"[WARN] Required Vault entry file not found: {f} (This is normal if not initialized yet)")
            all_exist = False
            
    sources_dir = os.path.join(vault_path, "01_Sources")
    if not os.path.exists(sources_dir):
        print("[*] No 01_Sources directory found. Skipping detailed Vault checks.")
        return all_exist
        
    analysis_dirs = [d for d in os.listdir(sources_dir) if d.endswith("_解析") and os.path.isdir(os.path.join(sources_dir, d))]
    
    if not analysis_dirs:
        print("[*] No active paper analysis directories (*_解析) found.")
        return all_exist

    success = True
    for adir in analysis_dirs:
        adir_path = os.path.join(sources_dir, adir)
        print(f"[*] Linting analysis folder: {adir}")
        
        expected_files = [
            "00_README.md",
            "01_Translation.md",
            "02_Logic_Flows.md",
            "03_Math_Equations.md",
            "04_Local_Glossary.md"
        ]
        
        for ef in expected_files:
            ef_path = os.path.join(adir_path, ef)
            if not os.path.exists(ef_path):
                print(f"  [ERROR] Missing expected file: {adir}/{ef}")
                success = False
                
        translation_path = os.path.join(adir_path, "01_Translation.md")
        images_dir = os.path.join(adir_path, "images")
        
        if os.path.exists(translation_path):
            with open(translation_path, "r", encoding="utf-8") as f:
                trans_content = f.read()
                
            img_links = re.findall(r"!\[.*?\]\((.*?)\)", trans_content)
            for link in img_links:
                if link.startswith("./") or link.startswith("../"):
                    clean_link = link.lstrip("./").lstrip("../")
                    if clean_link.startswith("images/"):
                        img_filename = clean_link.split("/")[-1]
                        actual_img_path = os.path.join(images_dir, img_filename)
                        if not os.path.exists(actual_img_path):
                            print(f"  [ERROR] Image link broken in 01_Translation.md: '{link}' (File not found at {actual_img_path})")
                            success = False
                    else:
                        print(f"  [WARN] Unexpected image link format in 01_Translation.md: '{link}'")

    if success:
        print("[SUCCESS] Vault structure verification passed.")
    else:
        print("[FAILED] Vault structure has integrity errors.")
    return success

if __name__ == "__main__":
    skill_ok = verify_skill_md()
    print("-" * 50)
    vault_ok = verify_vault_structure()
    
    if skill_ok and vault_ok:
        sys.exit(0)
    else:
        sys.exit(1)
