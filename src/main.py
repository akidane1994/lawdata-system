import os
import datetime
from api_client import fetch_law_data
from converter import json_to_markdown
from diff_generator import generate_diff_markdown

# パス設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "target_laws.txt")
LAWS_DIR = os.path.join(BASE_DIR, "laws")
CHANGES_DIR = os.path.join(BASE_DIR, "changes")

# 保存先作成
os.makedirs(LAWS_DIR, exist_ok=True)

def main():
    print("--- 法令更新チェック開始 ---")
    
    # 1. 対象リスト読み込み
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file not found: {CONFIG_FILE}")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        law_ids = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for law_id in law_ids:
        print(f"\nProcessing LawID: {law_id} ...")
        
        # 2. APIデータ取得
        json_data = fetch_law_data(law_id)
        if not json_data:
            print("Skipping due to fetch error.")
            continue

        # 3. Markdown変換
        new_md_text, law_name = json_to_markdown(json_data)
        if not new_md_text:
            print("Conversion failed.")
            continue

        file_name = f"{law_name}.md"
        file_path = os.path.join(LAWS_DIR, file_name)
        
        # 4. 既存ファイルとの比較 & 更新
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                old_md_text = f.read()
            
            # 差分チェック (簡易的な文字列比較)
            if old_md_text != new_md_text:
                print(f"Update detected for {law_name}!")
                
                # 新旧対照表の作成
                diff_md = generate_diff_markdown(old_md_text, new_md_text, law_name)
                
                if diff_md:
                    today = datetime.date.today().strftime("%Y-%m")
                    diff_dir = os.path.join(CHANGES_DIR, today)
                    os.makedirs(diff_dir, exist_ok=True)
                    
                    diff_file = os.path.join(diff_dir, f"{law_name}_diff.md")
                    with open(diff_file, "w", encoding="utf-8") as f:
                        f.write(diff_md)
                    print(f"Diff saved to: {diff_file}")

                # 最新版を上書き保存
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_md_text)
                print(f"Updated {file_name}")
            else:
                print(f"No changes for {law_name}.")
        else:
            # 新規作成
            print(f"New law detected: {law_name}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_md_text)

    print("\n--- 全処理完了 ---")

if __name__ == "__main__":
    main()