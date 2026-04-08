import sys
import os
from underthesea import dependency_parse

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.file_io import read_text, write_json

# Đường dẫn file đầu vào và đầu ra
INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "clauses.txt")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "output", "srl_results.json")

def get_subtree(node_id, deps):
    """
    Đệ quy lấy toàn bộ các từ phụ thuộc (subtree) của một node trên cây cú pháp.
    node_id: ID bắt đầu từ 1.
    """
    children = [node_id]
    for i, (word, head_id, dep_label) in enumerate(deps):
        curr_id = i + 1
        if head_id == node_id: # Nếu từ này phụ thuộc vào node hiện tại
            children.extend(get_subtree(curr_id, deps)) # Đệ quy lấy con của nó
    return children

def extract_srl_roles(clause):
    deps = dependency_parse(clause)
    srl_info = {"predicate": "", "roles": {}}
    
    # 1. Tìm từ gốc (Root) của cả câu
    root_id = -1
    for i, (word, head_id, dep_label) in enumerate(deps):
        if dep_label == "root":
            root_id = i + 1
            srl_info["predicate"] = word
            break
            
    if root_id == -1: return srl_info

    # 2. Xử lý riêng cho câu có hệ từ "là" (Ví dụ: Bên A là Công ty...)
    is_copula = False
    cop_id = -1
    for i, (word, head_id, dep_label) in enumerate(deps):
        if dep_label == "cop" and head_id == root_id:
            srl_info["predicate"] = "là"
            is_copula = True
            cop_id = i + 1
            break

    # -- TÌM CÂY CON CỦA CHỦ NGỮ (Để dùng cho kỹ thuật Subtree Subtraction sau này) --
    subj_subtree_ids = []
    for i, (word, head_id, dep_label) in enumerate(deps):
        if head_id == root_id and dep_label in ["nsubj", "nsubj:nn", "nsubj:pass"]:
            subj_subtree_ids.extend(get_subtree(i + 1, deps))

    # 3. Trích xuất các vai trò chính dựa trên các nhánh phụ thuộc trực tiếp vào Root
    for i, (word, head_id, dep_label) in enumerate(deps):
        curr_id = i + 1
        
        if head_id == root_id:
            subtree_ids = get_subtree(curr_id, deps)
            
            # -- LUẬT CONTIGUOUS SPAN (Cứu các từ viết tắt như TP.HCM, UBND bị rớt) --
            max_id = max(subtree_ids)
            while max_id < len(deps):
                next_word, _, next_label = deps[max_id]
                # Nếu từ tiếp theo bị nhầm là dấu câu (punct) nhưng có chứa chữ cái/số
                if next_label in ["punct", "conj"] and any(c.isalnum() for c in next_word):
                    subtree_ids.append(max_id + 1)
                    max_id += 1
                else:
                    break
                    
            subtree_ids.sort()
            phrase = " ".join([deps[idx - 1][0].replace('_', ' ') for idx in subtree_ids]).strip(" ,.")
            
            # Ánh xạ nhãn Dependency sang nhãn Semantic Role
            if dep_label in ["nsubj", "nsubj:nn"]:
                srl_info["roles"]["Agent"] = phrase
                
            elif dep_label in ["obj", "nsubj:pass"]: 
                srl_info["roles"]["Theme"] = phrase
                
            elif "tmod" in dep_label or (dep_label == "obl" and "ngày" in phrase.lower()):
                srl_info["roles"]["Time"] = phrase
                
            elif dep_label == "obl" and "ngày" not in phrase.lower():
                # Phân loại giới từ để gán đúng Location hoặc Manner
                first_word = phrase.split()[0].lower() if phrase else ""
                if first_word in ["tại", "ở", "trong", "trên"]:
                    srl_info["roles"]["Location"] = phrase
                elif first_word in ["với", "bằng"]:
                    srl_info["roles"]["Manner"] = phrase
                else:
                    srl_info["roles"]["Attribute"] = phrase
                    
            elif dep_label == "advcl": 
                srl_info["roles"]["Condition"] = phrase

    # -- LUẬT SUBTREE SUBTRACTION (Lấy Theme chuẩn xác cho câu "là") --
    if is_copula and "Theme" not in srl_info["roles"]:
        all_root_ids = get_subtree(root_id, deps)
        
        # Theme = Lấy toàn bộ cây Root TRỪ ĐI cây Chủ Ngữ và chữ "là"
        theme_ids = [idx for idx in all_root_ids if idx not in subj_subtree_ids and idx != cop_id]
        theme_ids.sort()
        
        # Lọc bỏ các dấu phẩy/chấm bị dư ở cuối chuỗi
        while theme_ids and not any(c.isalnum() for c in deps[theme_ids[-1]-1][0]):
            theme_ids.pop()
            
        if theme_ids:
            phrase = " ".join([deps[idx - 1][0].replace('_', ' ') for idx in theme_ids]).strip(" ,.")
            srl_info["roles"]["Theme"] = phrase

    return srl_info

def main():
    text = read_text(INPUT_PATH)
    if not text: 
        print("[srl_model] Lỗi: Không tìm thấy dữ liệu đầu vào.")
        return
    
    clauses = [c.strip() for c in text.split('\n') if c.strip()]
    results = []
    
    for clause in clauses:
        srl_data = extract_srl_roles(clause)
        if srl_data["predicate"]: # Chỉ lưu kết quả nếu câu có vị ngữ
            results.append({
                "clause": clause,
                "predicate": srl_data["predicate"],
                "roles": srl_data["roles"]
            })
            
    write_json(OUTPUT_PATH, results)
    print(f"[srl_model] Hoàn tất SRL! Kết quả sạch đã được lưu vào {OUTPUT_PATH}")

if __name__ == "__main__":
    main()