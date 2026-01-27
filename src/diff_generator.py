import re
import difflib

def split_into_articles(md_text):
    """Markdownテキストを条文ごとの辞書に分割する"""
    articles = {}
    current_article = None
    buffer = []
    
    # 条文見出しの正規表現 (例: **第一条...**)
    article_pattern = re.compile(r"^\*\*(第.+?条)(.*?)\*\*$")

    for line in md_text.splitlines():
        match = article_pattern.match(line)
        if match:
            # 前の条文を保存
            if current_article:
                articles[current_article] = "\n".join(buffer).strip()
            
            # 新しい条文開始
            current_article = match.group(1) # "第一条"
            # キャプションも含める場合は match.group(0) をキーにする等の工夫が可能
            buffer = [line]
        else:
            if current_article:
                buffer.append(line)
    
    # 最後の条文を保存
    if current_article:
        articles[current_article] = "\n".join(buffer).strip()
        
    return articles

def generate_diff_markdown(old_text, new_text, law_name):
    """新旧テキストから差分テーブルを作成する"""
    old_articles = split_into_articles(old_text)
    new_articles = split_into_articles(new_text)
    
    all_keys = sorted(list(set(old_articles.keys()) | set(new_articles.keys())))
    
    diff_rows = []
    
    for key in all_keys:
        old_content = old_articles.get(key, "(規定なし)")
        new_content = new_articles.get(key, "(削除)")
        
        # 空白削除して比較（フォーマット変更による誤検知を防ぐため）
        if old_content.replace(" ", "") != new_content.replace(" ", ""):
            # 改行を<br>に変換してテーブル内で表示できるようにする
            old_display = old_content.replace("\n", "<br>")
            new_display = new_content.replace("\n", "<br>")
            
            # テーブル行に追加
            diff_rows.append(f"| {key} | {old_display} | {new_display} |")

    if not diff_rows:
        return None # 差分なし

    # Markdownテーブルの組み立て
    header = f"# {law_name} 新旧対照表\n\n| 条数 | 旧規定 | 新規定 |\n| :--- | :--- | :--- |\n"
    return header + "\n".join(diff_rows)