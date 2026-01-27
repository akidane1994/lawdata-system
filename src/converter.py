def get_node_text(node):
    """ノード内のテキストを結合して取得"""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        children = node.get("children", [])
        return "".join([get_node_text(child) for child in children])
    return ""

def json_to_markdown(data):
    """e-Gov法令JSONデータをMarkdownテキストに変換する"""
    law_full_text = data.get("law_full_text", {})
    law_info = data.get("law_info", {})
    
    # ルート要素の探索
    law_body = None
    children_root = law_full_text.get("children", [])
    for child in children_root:
        if isinstance(child, dict) and child.get("tag") == "LawBody":
            law_body = child
            break
            
    if not law_body:
        return None, "法令解析エラー"

    # 法令名などの取得
    law_title_text = "法令名不明"
    main_provision = None
    
    for child in law_body.get("children", []):
        if isinstance(child, str): continue
        
        tag = child.get("tag")
        if tag == "LawTitle":
            law_title_text = get_node_text(child)
        elif tag == "MainProvision":
            main_provision = child

    md_lines = []
    md_lines.append(f"# {law_title_text}")
    md_lines.append(f"**法令番号:** {law_info.get('law_num', '不明')}")
    md_lines.append(f"**最終更新:** {data.get('revision_info', {}).get('updated', '')}")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    if not main_provision:
        return "\n".join(md_lines), law_title_text

    # 再帰処理関数
    def process_node(node, depth=0):
        # ★追加: 文字列の場合は処理せず戻る（エラー回避）
        if isinstance(node, str):
            return

        tag = node.get("tag")
        children = node.get("children", [])

        # 見出し (編・章など)
        if tag in ["Part", "Chapter", "Section", "Subsection", "Division"]:
            # タイトルタグを探す
            title_node = next((c for c in children if isinstance(c, dict) and c.get("tag") == f"{tag}Title"), None)
            if title_node:
                title_text = get_node_text(title_node)
                level = "#" * (min(depth + 2, 6))
                md_lines.append(f"\n{level} {title_text}\n")
            
            for child in children:
                # ★追加: 文字列チェック
                if isinstance(child, dict) and child.get("tag") != f"{tag}Title":
                    process_node(child, depth + 1)

        # 条文 (Article)
        elif tag == "Article":
            title_node = next((c for c in children if isinstance(c, dict) and c.get("tag") == "ArticleTitle"), None)
            title_str = get_node_text(title_node) if title_node else ""
            
            caption_node = next((c for c in children if isinstance(c, dict) and c.get("tag") == "ArticleCaption"), None)
            caption_str = f" {get_node_text(caption_node)}" if caption_node else ""

            # 条文見出し
            md_lines.append(f"**{title_str}{caption_str}**")

            # Paragraph(項), Item(号) の処理
            for child in children:
                if isinstance(child, str): continue # ★追加: 文字列スキップ

                c_tag = child.get("tag")
                if c_tag == "Paragraph":
                    p_num_node = next((c for c in child.get("children", []) if isinstance(c, dict) and c.get("tag") == "ParagraphNum"), None)
                    p_num = get_node_text(p_num_node)
                    
                    p_sent_node = next((c for c in child.get("children", []) if isinstance(c, dict) and c.get("tag") == "ParagraphSentence"), None)
                    p_text = get_node_text(p_sent_node)
                    
                    md_lines.append(f"{p_num} {p_text}")

                    # 号(Item)
                    for p_child in child.get("children", []):
                        if isinstance(p_child, dict) and p_child.get("tag") == "Item":
                            item_title = get_node_text(next((c for c in p_child.get("children", []) if isinstance(c, dict) and c.get("tag") == "ItemTitle"), None))
                            item_sent = get_node_text(next((c for c in p_child.get("children", []) if isinstance(c, dict) and c.get("tag") == "ItemSentence"), None))
                            md_lines.append(f"- {item_title} {item_sent}")
            
            md_lines.append("") # 空行

        else:
            # その他のタグは掘り下げる
            for child in children:
                process_node(child, depth)

    process_node(main_provision)
    return "\n".join(md_lines), law_title_text