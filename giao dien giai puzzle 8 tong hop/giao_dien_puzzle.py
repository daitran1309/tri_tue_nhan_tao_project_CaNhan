# -*- coding: utf-8 -*-
"""
=============================================================================
   CHƯƠNG TRÌNH GIẢI TRÒ CHƠI 8-PUZZLE TRỰC QUAN (GUI TKINTER)
   Môn học: Trí tuệ nhân tạo
   Sinh viên thực hiện: Trần Phước Đại (MSSV: 24110190)
=============================================================================
   Các tính năng chính:
   1. Giao diện trực quan hiện đại: Trạng thái đầu, Trạng thái đích và Puzzle hiện tại.
   2. Bộ sinh đề ngẫu nhiên (Shuffle): Luôn đảm bảo giải được (Solvable).
   3. Tích hợp 3 thuật toán cốt lõi: BFS, DFS, IDS sát với lý thuyết đã học.
   4. Trình diễn đường đi kết quả: Cho phép di chuyển từng bước (Lùi/Tiến) hoặc
      chạy tự động (Auto Play) với thanh điều chỉnh tốc độ mượt mà.
   5. Chạy đa luồng (Threading): Giúp giao diện không bị treo khi giải.
   6. Bảng nhật ký Trace Log & Thống kê sinh động trực quan.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
import heapq
from collections import deque
from ucs_solver import UCS_Solver, tinh_so_o_trung

# =============================================================================
# CẤU HÌNH & HẰNG SỐ HỆ THỐNG
# =============================================================================
# Trạng thái đích tiêu chuẩn
GOAL_STATE = [1, 2, 3,
              4, 5, 6,
              7, 8, 0]

# Màu sắc giao diện (Premium Palette)
COLOR_BG = "#F5F5F3"          # Màu nền sáng nhẹ của app
COLOR_CARD = "#FAF9F5"        # Màu nền của các ô số
COLOR_EMPTY = "#EAE8E3"       # Màu nền ô trống (0)
COLOR_TEXT_MAIN = "#2D2C2A"   # Màu chữ số chính
COLOR_ACCENT = "#4F4E4B"      # Màu xám tiêu đề
COLOR_SUCCESS = "#2E7D32"     # Màu xanh lá khi thành công
COLOR_BTN_PRIMARY = "#E5E4E0" # Màu nút chức năng mặc định
COLOR_BTN_ACTIVE = "#D5D4D0"  # Màu nút khi rê chuột qua

# =============================================================================
# PHẦN 1: LOGIC THUẬT TOÁN 8-PUZZLE (KHỚP HOÀN TOÀN VỚI BÀI HỌC)
# =============================================================================

def tao_node(state, duong_di, do_sau=0):
    """
    Tạo cấu trúc Node lưu trữ trạng thái của Puzzle.
    """
    return {
        "state": state,        # Mảng 9 số biểu diễn trạng thái
        "duong_di": duong_di,  # Danh sách các state đi qua từ đầu đến node này
        "do_sau": do_sau       # Độ sâu của node (dành cho DFS và IDS)
    }

def tinh_so_o_sai_khac(state, goal_state):
    """
    Tính số lượng ô sai vị trí (Misplaced Tiles) giữa trạng thái hiện tại và đích.
    Không tính ô trống 0.
    """
    return sum(1 for s, g in zip(state, goal_state) if s != 0 and s != g)

def tinh_khoang_cach_manhattan(state, goal_state):
    """
    Tính tổng khoảng cách Manhattan từ các ô số đến vị trí đích của chúng.
    Không tính ô trống 0.
    """
    distance = 0
    for i, val in enumerate(state):
        if val != 0:
            # Vị trí hiện tại (dòng, cột)
            r_curr, c_curr = i // 3, i % 3
            # Vị trí đích (dòng, cột)
            idx_goal = goal_state.index(val)
            r_goal, c_goal = idx_goal // 3, idx_goal % 3
            distance += abs(r_curr - r_goal) + abs(c_curr - c_goal)
    return distance

def EXPAND(node):
    """
    Mở rộng node hiện tại bằng cách di chuyển ô trống (0) theo 4 hướng:
    Lên, Xuống, Trái, Phải.
    """
    state = node["state"]
    vi_tri_trong = state.index(0)   # Tìm vị trí ô trống
    hang = vi_tri_trong // 3
    cot  = vi_tri_trong % 3

    cac_con = []
    
    # Định nghĩa 4 hướng di chuyển: (Hàng mới, Cột mới)
    huong = [
        (hang - 1, cot),   # Lên
        (hang + 1, cot),   # Xuống
        (hang,     cot - 1),  # Trái
        (hang,     cot + 1),  # Phải
    ]

    for hang_moi, cot_moi in huong:
        # Kiểm tra nước đi có nằm trong phạm vi bảng 3x3 không
        if 0 <= hang_moi < 3 and 0 <= cot_moi < 3:
            vi_tri_moi = hang_moi * 3 + cot_moi
            
            # Tạo bản sao của state và hoán đổi vị trí ô trống với ô bên cạnh
            state_moi = state.copy()
            state_moi[vi_tri_trong] = state_moi[vi_tri_moi]
            state_moi[vi_tri_moi]  = 0
            
            # Lưu đường đi mới
            duong_di_moi = node["duong_di"] + [state_moi]
            child = tao_node(state_moi, duong_di_moi, node["do_sau"] + 1)
            cac_con.append(child)

    return cac_con

def IS_CYCLE(node):
    """
    Kiểm tra xem trạng thái hiện tại đã xuất hiện trong đường đi trước đó hay chưa.
    Giúp phát hiện chu trình (lặp vô tận) đặc biệt hữu ích cho DLS/IDS.
    """
    state_hien_tai = node["state"]
    duong_di_truoc = node["duong_di"][:-1]  # Trừ state cuối cùng chính là nó
    return state_hien_tai in duong_di_truoc

# -----------------------------------------------------------------------------
# THUẬT TOÁN 1: BFS - Graph Search (Tìm kiếm theo chiều rộng)
# -----------------------------------------------------------------------------
def BFS_Solver(trang_thai_dau, trang_thai_dich, log_callback=None, stop_flag=None):
    """
    Giải 8-puzzle bằng thuật toán BFS.
    Sử dụng deque làm FIFO Queue và Set để tối ưu hóa tốc độ tìm kiếm.
    """
    node_dau = tao_node(trang_thai_dau, [trang_thai_dau])
    
    if trang_thai_dau == trang_thai_dich:
        return node_dau["duong_di"], 1
        
    frontier = deque([node_dau])
    explored = set()
    frontier_states = {tuple(trang_thai_dau)}
    
    dem_node = 0
    
    while frontier:
        # Kiểm tra xem người dùng có yêu cầu dừng ngang không
        if stop_flag and stop_flag():
            return None, dem_node

        node = frontier.popleft()
        state_tuple = tuple(node["state"])
        frontier_states.discard(state_tuple)
        explored.add(state_tuple)
        
        dem_node += 1
        
        # Log chi tiết các bước Pop/Explored theo yêu cầu của học viên
        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: {node['state']}")
                log_callback(f"EXPLORED: {node['state']}")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu để tránh giật lag UI) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[BFS] Đang xét node thứ {dem_node}... (Frontier: {len(frontier)})")
            
        for child in EXPAND(node):
            child_state = child["state"]
            child_tuple = tuple(child_state)
            
            if child_tuple not in explored and child_tuple not in frontier_states:
                # Log chi tiết bước Push Frontier
                if log_callback and dem_node <= 100:
                    log_callback(f"  PUSH FRONTIER: {child_state}")
                    
                if child_state == trang_thai_dich:
                    if log_callback:
                        log_callback(f"[BFS] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
                    return child["duong_di"], dem_node
                    
                frontier.append(child)
                frontier_states.add(child_tuple)
                
    return None, dem_node

# -----------------------------------------------------------------------------
# THUẬT TOÁN 2: DFS - Graph Search (Tìm kiếm theo chiều sâu có giới hạn)
# -----------------------------------------------------------------------------
def DFS_Solver(trang_thai_dau, trang_thai_dich, gioi_han_do_sau=25, log_callback=None, stop_flag=None):
    """
    Giải 8-puzzle bằng thuật toán DFS sử dụng ngăn xếp Stack.
    Cần giới hạn độ sâu (Depth Limit) để tránh treo bộ nhớ do nhánh đệ quy vô hạn.
    """
    node_dau = tao_node(trang_thai_dau, [trang_thai_dau], do_sau=0)
    
    if trang_thai_dau == trang_thai_dich:
        return node_dau["duong_di"], 1
        
    frontier = [node_dau]
    explored = set()
    frontier_states = {tuple(trang_thai_dau)}
    
    dem_node = 0
    
    while frontier:
        if stop_flag and stop_flag():
            return None, dem_node

        node = frontier.pop()  # LIFO: lấy ra phần tử cuối stack
        state_tuple = tuple(node["state"])
        frontier_states.discard(state_tuple)
        explored.add(state_tuple)
        
        dem_node += 1
        
        # Log chi tiết các bước Pop/Explored theo yêu cầu của học viên
        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: {node['state']} (độ sâu d = {node['do_sau']})")
                log_callback(f"EXPLORED: {node['state']}")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu để tránh giật lag UI) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[DFS] Đang xét node thứ {dem_node} ở độ sâu d = {node['do_sau']}...")
            
        if node["state"] == trang_thai_dich:
            if log_callback:
                log_callback(f"[DFS] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
            return node["duong_di"], dem_node
            
        if node["do_sau"] >= gioi_han_do_sau:
            continue
            
        for child in EXPAND(node):
            child_state = child["state"]
            child_tuple = tuple(child_state)
            
            if child_tuple not in explored and child_tuple not in frontier_states:
                # Log chi tiết bước Push Frontier
                if log_callback and dem_node <= 100:
                    log_callback(f"  PUSH FRONTIER: {child_state}")
                    
                frontier.append(child)
                frontier_states.add(child_tuple)
                
    return None, dem_node

# -----------------------------------------------------------------------------
# THUẬT TOÁN 3: IDS (Iterative Deepening Search - Tìm kiếm sâu dần)
# -----------------------------------------------------------------------------
def DLS(trang_thai_dau, trang_thai_dich, gioi_han_do_sau, dem_node, log_callback=None, stop_flag=None):
    """
    Depth-Limited Search sử dụng trong thuật toán IDS.
    Sử dụng hàm IS_CYCLE để tránh đi vào vòng lặp vô hạn.
    """
    node_dau = tao_node(trang_thai_dau, [trang_thai_dau], do_sau=0)
    frontier = [node_dau]  # Stack LIFO
    
    result = "failure"
    
    while frontier:
        if stop_flag and stop_flag():
            return "failure"

        node = frontier.pop()
        dem_node[0] += 1
        
        # Log chi tiết các bước Pop/Explored theo yêu cầu của học viên
        if log_callback:
            if dem_node[0] <= 100:
                log_callback(f"POP: {node['state']} (độ sâu d = {node['do_sau']})")
                log_callback(f"EXPLORED: {node['state']}")
            elif dem_node[0] == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu để tránh giật lag UI) ...")
        
        if node["state"] == trang_thai_dich:
            return node
            
        if node["do_sau"] > gioi_han_do_sau:
            result = "cutoff"
        elif not IS_CYCLE(node):
            for child in EXPAND(node):
                # Log chi tiết bước Push Frontier
                if log_callback and dem_node[0] <= 100:
                    log_callback(f"  PUSH FRONTIER: {child['state']}")
                frontier.append(child)
                
    return result

def IDS_Solver(trang_thai_dau, trang_thai_dich, log_callback=None, stop_flag=None):
    """
    Giải 8-puzzle bằng thuật toán IDS.
    Lặp tăng dần độ sâu d từ 0 trở đi cho tới khi tìm thấy lời giải.
    """
    dem_node = [0]
    depth = 0
    
    while True:
        if stop_flag and stop_flag():
            return None, dem_node[0]

        if log_callback:
            log_callback(f"[IDS] Đang chạy DLS với độ sâu giới hạn l = {depth}")
            
        result = DLS(trang_thai_dau, trang_thai_dich, depth, dem_node, log_callback, stop_flag)
        
        if result == "cutoff":
            if log_callback:
                log_callback(f"  → Bị cutoff! Tăng độ sâu giới hạn lên d = {depth + 1}\n")
            depth += 1
            if depth > 20: # Giới hạn bảo vệ ứng dụng nếu shuffle quá phức tạp
                if log_callback:
                    log_callback("[IDS] Đạt độ sâu tối đa 20! Dừng tìm kiếm để bảo vệ luồng.")
                return None, dem_node[0]
            continue
            
        if result == "failure":
            if log_callback:
                log_callback("[IDS] Thất bại! Không có lời giải.")
            return None, dem_node[0]
            
        # Nếu result là một node chứa lời giải
        if log_callback:
            log_callback(f"[IDS] TÌM THẤY LỜI GIẢI ở độ sâu d = {depth}!")
        return result["duong_di"], dem_node[0]


# -----------------------------------------------------------------------------
# THUẬT TOÁN 4: GREEDY BEST-FIRST SEARCH (Tìm kiếm tham lam)
# -----------------------------------------------------------------------------
def Greedy_Solver(trang_thai_dau, trang_thai_dich, heuristic_type="manhattan", log_callback=None, stop_flag=None):
    """
    Giải 8-puzzle bằng thuật toán Greedy Best-First Search.
    Frontier sắp xếp theo h(n) tăng dần.
    """
    if heuristic_type == "manhattan":
        h_func = tinh_khoang_cach_manhattan
        h_name = "Manhattan"
    else:
        h_func = tinh_so_o_sai_khac
        h_name = "Số ô sai"
        
    h_dau = h_func(trang_thai_dau, trang_thai_dich)
    node_dau = {
        "state": trang_thai_dau,
        "duong_di": [trang_thai_dau],
        "do_sau": 0,
        "h": h_dau
    }
    
    if trang_thai_dau == trang_thai_dich:
        return node_dau["duong_di"], 1
        
    counter = 0
    frontier = []
    heapq.heappush(frontier, (node_dau["h"], counter, node_dau))
    
    explored = set()
    frontier_states = {tuple(trang_thai_dau)}
    
    dem_node = 0
    
    while frontier:
        if stop_flag and stop_flag():
            return None, dem_node
            
        h_val, _, node = heapq.heappop(frontier)
        state_tuple = tuple(node["state"])
        
        if state_tuple in explored:
            continue
            
        frontier_states.discard(state_tuple)
        explored.add(state_tuple)
        dem_node += 1
        
        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: {node['state']} (h = {node['h']})")
                log_callback(f"EXPLORED: {node['state']}")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu để tránh giật lag UI) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[Greedy-{h_name}] Đang xét node thứ {dem_node}... (Frontier: {len(frontier)})")
                
        if node["state"] == trang_thai_dich:
            if log_callback:
                log_callback(f"[Greedy-{h_name}] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
            return node["duong_di"], dem_node
            
        for child in EXPAND(node):
            child_state = child["state"]
            child_tuple = tuple(child_state)
            
            if child_tuple not in explored and child_tuple not in frontier_states:
                h_child = h_func(child_state, trang_thai_dich)
                child["h"] = h_child
                
                if log_callback and dem_node <= 100:
                    log_callback(f"  PUSH FRONTIER: {child_state} (h = {h_child})")
                    
                counter += 1
                heapq.heappush(frontier, (h_child, counter, child))
                frontier_states.add(child_tuple)
                
    return None, dem_node


# -----------------------------------------------------------------------------
# THUẬT TOÁN 5: A* SEARCH (Tìm kiếm A sao)
# -----------------------------------------------------------------------------
def AStar_Solver(trang_thai_dau, trang_thai_dich, heuristic_type="manhattan", log_callback=None, stop_flag=None):
    """
    Giải 8-puzzle bằng thuật toán A* Search.
    Frontier sắp xếp theo f(n) = g(n) + h(n) tăng dần.
    """
    if heuristic_type == "manhattan":
        h_func = tinh_khoang_cach_manhattan
        h_name = "Manhattan"
    else:
        h_func = tinh_so_o_sai_khac
        h_name = "Số ô sai"
        
    h_dau = h_func(trang_thai_dau, trang_thai_dich)
    node_dau = {
        "state": trang_thai_dau,
        "duong_di": [trang_thai_dau],
        "do_sau": 0,
        "h": h_dau,
        "f": h_dau
    }
    
    if trang_thai_dau == trang_thai_dich:
        return node_dau["duong_di"], 1
        
    counter = 0
    frontier = []
    heapq.heappush(frontier, (node_dau["f"], node_dau["h"], counter, node_dau))
    
    explored = {}
    frontier_states = {tuple(trang_thai_dau): node_dau["do_sau"]}
    
    dem_node = 0
    
    while frontier:
        if stop_flag and stop_flag():
            return None, dem_node
            
        f_val, h_val, _, node = heapq.heappop(frontier)
        state_tuple = tuple(node["state"])
        
        if state_tuple in explored and explored[state_tuple] <= node["do_sau"]:
            continue
            
        explored[state_tuple] = node["do_sau"]
        dem_node += 1
        
        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: {node['state']} (g = {node['do_sau']} | h = {node['h']} | f = {node['f']})")
                log_callback(f"EXPLORED: {node['state']}")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu để tránh giật lag UI) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[A*-{h_name}] Đang xét node thứ {dem_node}... (Frontier: {len(frontier)})")
                
        if node["state"] == trang_thai_dich:
            if log_callback:
                log_callback(f"[A*-{h_name}] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
            return node["duong_di"], dem_node
            
        for child in EXPAND(node):
            child_state = child["state"]
            child_tuple = tuple(child_state)
            g_child = child["do_sau"]
            
            if child_tuple not in explored or g_child < explored[child_tuple]:
                if child_tuple in frontier_states and frontier_states[child_tuple] <= g_child:
                    continue
                    
                h_child = h_func(child_state, trang_thai_dich)
                f_child = g_child + h_child
                child["h"] = h_child
                child["f"] = f_child
                
                if log_callback and dem_node <= 100:
                    log_callback(f"  PUSH FRONTIER: {child_state} (g = {g_child} | h = {h_child} | f = {f_child})")
                    
                counter += 1
                heapq.heappush(frontier, (f_child, h_child, counter, child))
                frontier_states[child_tuple] = g_child
                
    return None, dem_node


# -----------------------------------------------------------------------------
# BỘ SHUFFLE (Sinh đề ngẫu nhiên đảm bảo luôn giải được)
# -----------------------------------------------------------------------------
def sinh_de_ngau_nhien(goal_state, so_buoc=14):
    """
    Bắt đầu từ trạng thái Đích, thực hiện di chuyển ô trống ngẫu nhiên
    để tạo ra đề bài. Phương pháp này đảm bảo 100% đề bài sinh ra đều GIẢI ĐƯỢC
    và lời giải nằm trong phạm vi 14 bước đổ lại (giúp tìm kiếm trong < 0.1s).
    """
    state = goal_state.copy()
    vi_tri_cu = -1
    
    for _ in range(so_buoc):
        idx = state.index(0)
        hang = idx // 3
        cot = idx % 3
        
        nuoc_di_hop_le = []
        if hang > 0: nuoc_di_hop_le.append(idx - 3) # Lên
        if hang < 2: nuoc_di_hop_le.append(idx + 3) # Xuống
        if cot > 0: nuoc_di_hop_le.append(idx - 1)  # Trái
        if cot < 2: nuoc_di_hop_le.append(idx + 1)  # Phải
        
        # Tránh di chuyển quay ngược lại vị trí ô trống vừa đi ở bước trước
        if vi_tri_cu in nuoc_di_hop_le and len(nuoc_di_hop_le) > 1:
            nuoc_di_hop_le.remove(vi_tri_cu)
            
        next_idx = random.choice(nuoc_di_hop_le)
        state[idx], state[next_idx] = state[next_idx], state[idx]
        vi_tri_cu = idx
        
    return state


# =============================================================================
# PHẦN 2: THIẾT KẾ GIAO DIỆN ĐỒ HỌA TKINTER
# =============================================================================

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Trực quan - Trần Phước Đại (24110190)")
        # Rút ngắn chiều cao cửa sổ xuống 635px để đảm bảo hiển thị trọn vẹn trên mọi màn hình máy tính laptop học viên
        self.root.geometry("1120x635")
        self.root.configure(bg=COLOR_BG)
        
        # Biến trạng thái của ứng dụng
        self.trang_thai_dau = [2, 8, 3, 1, 6, 4, 7, 0, 5] # Mặc định giống đề bài trong BFS.ipynb
        self.duong_di_loi_giai = []
        self.index_buoc_hien_tai = 0
        self.dang_chay_giai = False
        self.dang_chay_auto = False
        self.flag_dung_giai = False
        
        # Thiết kế giao diện chính
        self.setup_styles()
        self.build_gui()
        
        # Hiển thị trạng thái ban đầu lên bảng
        self.update_puzzle_grids()

    def setup_styles(self):
        """
        Cài đặt các style hiện đại cho các widget Tkinter.
        """
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Cấu hình màu nền cho Combobox và Button
        self.style.configure("TCombobox", fieldbackground="white", background=COLOR_BTN_PRIMARY, font=("Segoe UI", 11))
        self.style.configure("TButton", font=("Segoe UI", 11), background=COLOR_BTN_PRIMARY, borderwidth=1)
        self.style.map("TButton", background=[("active", COLOR_BTN_ACTIVE)])

    def build_gui(self):
        """
        Xây dựng cấu trúc layout của chương trình.
        """
        # --- TIÊU ĐỀ CHƯƠNG TRÌNH ---
        title_frame = tk.Frame(self.root, bg=COLOR_BG, pady=5)
        title_frame.pack(fill=tk.X)
        
        lbl_title = tk.Label(title_frame, text="CHƯƠNG TRÌNH GIẢI 8-PUZZLE TRỰC QUAN", 
                             font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BG)
                             # Giảm font tiêu đề từ 20 xuống 16 để gom gọn kích thước
        lbl_title.pack()
        
        lbl_sub = tk.Label(title_frame, text="Học viên: Trần Phước Đại - MSSV: 24110190 - Lớp Trí tuệ nhân tạo", 
                            font=("Segoe UI", 9, "italic"), fg=COLOR_ACCENT, bg=COLOR_BG)
        lbl_sub.pack()

        # --- KHUNG NỘI DUNG CHÍNH (Chi tay đôi: Trái & Phải) ---
        main_container = tk.Frame(self.root, bg=COLOR_BG, padx=15, pady=5)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Cột Trái: Bảng game & Các nút điều khiển
        left_col = tk.Frame(main_container, bg=COLOR_BG)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Cột Phải: Nhật ký Trace log & Bảng thống kê (Tăng chiều rộng lên 430px để hiển thị log chi tiết rộng hơn)
        right_col = tk.Frame(main_container, bg=COLOR_BG, width=430)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(15, 0))
        right_col.pack_propagate(False)

        # =====================================================================
        # THIẾT KẾ CỘT TRÁI (GAMEPLAY & CONTROLS)
        # =====================================================================
        # Khung chứa 2 bảng phía trên: Bảng Trạng thái đầu & Bảng Đích
        top_grids_frame = tk.Frame(left_col, bg=COLOR_BG)
        top_grids_frame.pack(fill=tk.X, pady=(0, 5))

        # 1. Bảng Trạng thái đầu
        frame_start = tk.LabelFrame(top_grids_frame, text=" Trạng thái ban đầu ", 
                                    font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=8, pady=5)
        frame_start.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        self.start_tiles = []
        self.create_puzzle_grid_ui(frame_start, self.start_tiles)
        
        # Nút Shuffle đặt ngay dưới bảng trạng thái ban đầu (Giảm padding dọc từ 4 xuống 2)
        self.btn_shuffle = tk.Button(frame_start, text="🔄 Shuffle (Sinh đề ngẫu nhiên)", 
                                      font=("Segoe UI", 9, "bold"), bg="#E1DFDA", fg="#333", relief="flat",
                                      padx=8, pady=2, command=self.handle_shuffle)
        self.btn_shuffle.pack(pady=(5, 0))

        # Khung mũi tên chuyển đổi ở giữa (Giảm font từ 36 xuống 24)
        arrow_frame = tk.Frame(top_grids_frame, bg=COLOR_BG)
        arrow_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        lbl_arrow = tk.Label(arrow_frame, text="➔", font=("Segoe UI", 24), fg=COLOR_ACCENT, bg=COLOR_BG)
        lbl_arrow.pack(expand=True)

        # 2. Bảng Đích
        frame_goal = tk.LabelFrame(top_grids_frame, text=" Trạng thái Đích ", 
                                   font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=8, pady=5)
        frame_goal.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        self.goal_tiles = []
        self.create_puzzle_grid_ui(frame_goal, self.goal_tiles, is_goal=True)

        # 3. Khung bảng điều khiển thuật toán ở giữa
        control_panel = tk.LabelFrame(left_col, text=" Bảng điều khiển giải thuật ", 
                                      font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=12, pady=6)
        control_panel.pack(fill=tk.X, pady=5)

        # Combobox chọn thuật toán
        tk.Label(control_panel, text="Chọn thuật toán:", font=("Segoe UI", 10), bg=COLOR_BG).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.cbo_algo = ttk.Combobox(control_panel, values=[
            "BFS (Chiều rộng)", 
            "DFS (Chiều sâu)", 
            "IDS (Sâu dần)", 
            "UCS (Độ ưu tiên ô trùng)",
            "Greedy (Tham lam - Số ô sai)",
            "Greedy (Tham lam - Manhattan)",
            "A* (A sao - Số ô sai)",
            "A* (A sao - Manhattan)"
        ], state="readonly", width=25)
        self.cbo_algo.grid(row=0, column=1, padx=5, pady=3)
        self.cbo_algo.current(0) # Chọn mặc định là BFS

        # Nút Chạy giải thuật
        self.btn_solve = tk.Button(control_panel, text="▶ Chạy Giải", font=("Segoe UI", 10, "bold"), 
                                   bg="#4CAF50", fg="white", activebackground="#43A047", relief="flat", padx=10,
                                   command=self.start_solving_thread)
        self.btn_solve.grid(row=0, column=2, padx=10, pady=3)
        
        # Nút Dừng khẩn cấp
        self.btn_stop = tk.Button(control_panel, text="⏹ Dừng", font=("Segoe UI", 10, "bold"), 
                                  bg="#F44336", fg="white", activebackground="#E53935", relief="flat", padx=10,
                                  state=tk.DISABLED, command=self.stop_solving)
        self.btn_stop.grid(row=0, column=3, padx=5, pady=3)

        # Ngăn cách giữa hai nhóm nút (Giảm pady dọc xuống 6)
        separator = ttk.Separator(control_panel, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=5, sticky="ew", pady=6)

        # Dòng nút điều khiển kết quả: Lùi, Tiến, Auto, Reset
        result_buttons_frame = tk.Frame(control_panel, bg=COLOR_BG)
        result_buttons_frame.grid(row=2, column=0, columnspan=5, sticky="ew")
        
        self.btn_prev = tk.Button(result_buttons_frame, text="◀ Bước Lùi", font=("Segoe UI", 9), bg="#E1DFDA", relief="flat", padx=8, command=self.step_prev, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=3)
        
        self.btn_next = tk.Button(result_buttons_frame, text="Bước Tiến ▶", font=("Segoe UI", 9), bg="#E1DFDA", relief="flat", padx=8, command=self.step_next, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=3)
        
        self.btn_auto = tk.Button(result_buttons_frame, text="🔄 Chạy Auto", font=("Segoe UI", 9, "bold"), bg="#2196F3", fg="white", activebackground="#1E88E5", relief="flat", padx=8, command=self.toggle_auto_play, state=tk.DISABLED)
        self.btn_auto.pack(side=tk.LEFT, padx=5)

        self.btn_reset = tk.Button(result_buttons_frame, text="↻ Reset", font=("Segoe UI", 9), bg="#E1DFDA", relief="flat", padx=8, command=self.handle_reset, state=tk.DISABLED)
        self.btn_reset.pack(side=tk.LEFT, padx=3)

        # Thanh trượt tốc độ chạy tự động
        tk.Label(result_buttons_frame, text="Auto (ms):", font=("Segoe UI", 9), bg=COLOR_BG).pack(side=tk.LEFT, padx=(10, 3))
        self.scale_speed = tk.Scale(result_buttons_frame, from_=200, to=2000, orient=tk.HORIZONTAL, length=100, bg=COLOR_BG, highlightthickness=0, fg=COLOR_TEXT_MAIN)
        self.scale_speed.set(500) # Mặc định là 500ms
        self.scale_speed.pack(side=tk.LEFT)

        # 4. Bảng Puzzle hiện tại (nằm dưới cùng bên trái) (Giảm pady dọc xuống 6)
        frame_current = tk.LabelFrame(left_col, text=" Bảng chạy mô phỏng hiện tại ", 
                                      font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=12, pady=6)
        frame_current.pack(fill=tk.BOTH, expand=True, pady=(3, 0))
        
        self.current_tiles = []
        self.create_puzzle_grid_ui(frame_current, self.current_tiles)
        
        self.lbl_step_counter = tk.Label(frame_current, text="Trạng thái: Đang đợi giải...", 
                                         font=("Segoe UI", 10, "bold"), fg=COLOR_SUCCESS, bg=COLOR_BG)
        self.lbl_step_counter.pack(pady=(5, 0))

        # =====================================================================
        # THIẾT KẾ CỘT PHẢI (STATISTICS & TRACE LOGS)
        # =====================================================================
        # 1. Bảng thống kê (Giảm pady xuống 5)
        stats_frame = tk.LabelFrame(right_col, text=" Thống kê kết quả ", 
                                    font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=12, pady=5)
        stats_frame.pack(fill=tk.X, pady=(0, 5))

        self.lbl_stat_steps = tk.Label(stats_frame, text="• Số bước di chuyển: --", font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_stat_steps.pack(fill=tk.X, pady=2)

        self.lbl_stat_nodes = tk.Label(stats_frame, text="• Tổng số Node đã xét: --", font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_stat_nodes.pack(fill=tk.X, pady=2)

        self.lbl_stat_time = tk.Label(stats_frame, text="• Thời gian giải: --", font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_stat_time.pack(fill=tk.X, pady=2)

        # 2. Khung Trace log thuật toán
        trace_frame = tk.LabelFrame(right_col, text=" Trace Log - Nhật ký thuật toán ", 
                                    font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=8, pady=5)
        trace_frame.pack(fill=tk.BOTH, expand=True)

        self.text_log = tk.Text(trace_frame, wrap=tk.WORD, font=("Consolas", 8), bg="#FAF9F7", fg="#333", borderwidth=1, relief="solid")
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(trace_frame, command=self.text_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_log.config(yscrollcommand=scrollbar.set)
        
        self.log_message("Sẵn sàng! Nhấn 'Shuffle' để sinh đề hoặc nhấn 'Chạy Giải' để tìm lời giải ngay.")

    def create_puzzle_grid_ui(self, parent, tile_list, is_goal=False):
        """
        Hàm tạo giao diện bảng 3x3 chứa các ô số trượt.
        """
        grid_container = tk.Frame(parent, bg=COLOR_BG)
        grid_container.pack(expand=True)
        
        # Mảng hiển thị mặc định lúc vẽ ban đầu
        default_state = GOAL_STATE if is_goal else self.trang_thai_dau

        for i in range(9):
            row = i // 3
            col = i % 3
            val = default_state[i]
            
            # Thay đổi font chữ từ 20 xuống 14, chiều cao ô số từ 2 xuống 1 (height=1)
            # Giúp bảng cực kỳ nhỏ gọn, vừa khít hoàn hảo trên mọi kích thước màn hình
            tile = tk.Label(grid_container, text=str(val) if val != 0 else "", 
                            font=("Segoe UI", 14, "bold"), width=4, height=1,
                            bg=COLOR_CARD if val != 0 else COLOR_EMPTY,
                            fg=COLOR_TEXT_MAIN, relief="flat", bd=1,
                            highlightthickness=1, highlightbackground="#D4D3CF")
            tile.grid(row=row, column=col, padx=3, pady=3) # Rút nhỏ khoảng cách padx/pady xuống 3px
            tile_list.append(tile)

    # =====================================================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN GIAO DIỆN (UI EVENTS)
    # =====================================================================
    def log_message(self, text):
        """
        Ghi log nhật ký vào khung Trace Log và tự động cuộn xuống dưới.
        """
        self.text_log.insert(tk.END, text + "\n")
        self.text_log.see(tk.END)

    def update_puzzle_grids(self):
        """
        Cập nhật lại hình ảnh các số trên 3 bảng tương ứng với biến trạng thái.
        """
        # 1. Cập nhật Bảng ban đầu
        for i, val in enumerate(self.trang_thai_dau):
            self.start_tiles[i].config(text=str(val) if val != 0 else "",
                                       bg=COLOR_CARD if val != 0 else COLOR_EMPTY)
            
        # 2. Cập nhật Bảng chạy mô phỏng hiện tại
        state_hien_tai = self.trang_thai_dau
        if self.duong_di_loi_giai and 0 <= self.index_buoc_hien_tai < len(self.duong_di_loi_giai):
            state_hien_tai = self.duong_di_loi_giai[self.index_buoc_hien_tai]
            
        for i, val in enumerate(state_hien_tai):
            self.current_tiles[i].config(text=str(val) if val != 0 else "",
                                         bg=COLOR_CARD if val != 0 else COLOR_EMPTY)
            
        # Cập nhật nhãn đếm bước
        if not self.duong_di_loi_giai:
            self.lbl_step_counter.config(text="Trạng thái: Đang đợi giải...", fg=COLOR_ACCENT)
        else:
            total_steps = len(self.duong_di_loi_giai) - 1
            if self.index_buoc_hien_tai == 0:
                self.lbl_step_counter.config(text=f"Bước hiện tại: 0 / {total_steps} (Trạng thái đầu)", fg=COLOR_ACCENT)
            elif self.index_buoc_hien_tai == total_steps:
                self.lbl_step_counter.config(text=f"Bước hiện tại: {self.index_buoc_hien_tai} / {total_steps} (Hoàn thành đích! 🎉)", fg=COLOR_SUCCESS)
            else:
                self.lbl_step_counter.config(text=f"Bước hiện tại: {self.index_buoc_hien_tai} / {total_steps}", fg="#1E88E5")

    def handle_shuffle(self):
        """
        Xử lý khi người dùng nhấn nút Shuffle. Sinh ra một trạng thái đầu mới.
        """
        # Nếu đang chạy tự động thì dừng lại
        self.dang_chay_auto = False
        
        # Sinh trạng thái đầu mới ngẫu nhiên và giải được
        self.trang_thai_dau = sinh_de_ngau_nhien(GOAL_STATE, so_buoc=13)
        self.duong_di_loi_giai = []
        self.index_buoc_hien_tai = 0
        
        # Cập nhật UI
        self.update_puzzle_grids()
        
        # Reset thông số thống kê
        self.lbl_stat_steps.config(text="• Số bước di chuyển: --")
        self.lbl_stat_nodes.config(text="• Tổng số Node đã xét: --")
        self.lbl_stat_time.config(text="• Thời gian giải: --")
        
        # Reset trạng thái các nút điều khiển kết quả
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED, text="🔄 Chạy Auto")
        self.btn_reset.config(state=tk.DISABLED)
        
        self.text_log.delete('1.0', tk.END)
        self.log_message(f"Bảng vừa sinh ngẫu nhiên: {self.trang_thai_dau}")
        self.log_message("Nhấn nút 'Chạy Giải' để bắt đầu tìm kiếm lời giải.")

    def handle_reset(self):
        """
        Reset bảng chạy mô phỏng hiện tại về trạng thái ban đầu của lời giải.
        """
        self.index_buoc_hien_tai = 0
        self.dang_chay_auto = False
        self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")
        self.update_puzzle_grids()
        self.btn_prev.config(state=tk.DISABLED)
        if len(self.duong_di_loi_giai) > 1:
            self.btn_next.config(state=tk.NORMAL)

    def step_next(self):
        """
        Di chuyển tới 1 bước trong danh sách lời giải.
        """
        if self.duong_di_loi_giai and self.index_buoc_hien_tai < len(self.duong_di_loi_giai) - 1:
            self.index_buoc_hien_tai += 1
            self.update_puzzle_grids()
            self.btn_prev.config(state=tk.NORMAL)
            
            # Nếu chạm đích
            if self.index_buoc_hien_tai == len(self.duong_di_loi_giai) - 1:
                self.btn_next.config(state=tk.DISABLED)
                if self.dang_chay_auto:
                    self.dang_chay_auto = False
                    self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")

    def step_prev(self):
        """
        Lùi lại 1 bước trong danh sách lời giải.
        """
        if self.duong_di_loi_giai and self.index_buoc_hien_tai > 0:
            self.index_buoc_hien_tai -= 1
            self.update_puzzle_grids()
            self.btn_next.config(state=tk.NORMAL)
            
            # Nếu lùi về vạch xuất phát
            if self.index_buoc_hien_tai == 0:
                self.btn_prev.config(state=tk.DISABLED)

    def toggle_auto_play(self):
        """
        Chuyển đổi chế độ chạy tự động (Auto Play).
        """
        if not self.duong_di_loi_giai:
            return
            
        if self.dang_chay_auto:
            # Đang chạy thì bấm để dừng
            self.dang_chay_auto = False
            self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")
            self.log_message("[Auto] Đã tạm dừng chạy tự động.")
        else:
            # Đang dừng thì bấm để chạy tiếp
            self.dang_chay_auto = True
            self.btn_auto.config(text="⏸ Dừng Auto", bg="#FF9800")
            self.log_message("[Auto] Bắt đầu chạy tự động mô phỏng các bước...")
            
            # Nếu đang ở vị trí đích, tự động quay về từ đầu rồi chạy
            if self.index_buoc_hien_tai >= len(self.duong_di_loi_giai) - 1:
                self.index_buoc_hien_tai = 0
                self.update_puzzle_grids()
                
            self.run_auto_play_loop()

    def run_auto_play_loop(self):
        """
        Vòng lặp chạy tự động bằng cơ chế định thìafter của Tkinter để tránh treo app.
        """
        if not self.dang_chay_auto:
            return
            
        if self.index_buoc_hien_tai < len(self.duong_di_loi_giai) - 1:
            self.step_next()
            # Lấy giá trị ms hiện tại trên Slider trượt
            speed_ms = self.scale_speed.get()
            self.root.after(speed_ms, self.run_auto_play_loop)
        else:
            # Đã đi tới đích
            self.dang_chay_auto = False
            self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")
            self.log_message("[Auto] Hoàn thành trình diễn lời giải!")

    # =====================================================================
    # XỬ LÝ KHÁM PHÁ THUẬT TOÁN ĐA LUỒNG (THREADING)
    # =====================================================================
    def start_solving_thread(self):
        """
        Khởi động luồng phụ chạy thuật toán tìm kiếm lời giải.
        """
        if self.trang_thai_dau == GOAL_STATE:
            messagebox.showinfo("Thông báo", "Bảng hiện tại đã ở trạng thái Đích rồi!")
            return

        self.dang_chay_giai = True
        self.flag_dung_giai = False
        self.text_log.delete('1.0', tk.END)
        
        # Thay đổi trạng thái các nút
        self.btn_solve.config(state=tk.DISABLED, text="⌛ Đang tìm...")
        self.btn_shuffle.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.DISABLED)
        
        # Khởi chạy luồng phụ
        threading.Thread(target=self.solve_puzzle, daemon=True).start()

    def stop_solving(self):
        """
        Nút dừng khẩn cấp khi thuật toán đang tìm kiếm.
        """
        if self.dang_chay_giai:
            self.flag_dung_giai = True
            self.log_message("\n⚠️ ĐANG YÊU CẦU DỪNG TÌM KIẾM KHẨN CẤP...")

    def check_stop_flag(self):
        """
        Trả về True nếu người dùng yêu cầu dừng khẩn cấp.
        """
        return self.flag_dung_giai

    def solve_puzzle(self):
        """
        Thực hiện tìm kiếm lời giải dựa trên thuật toán được chọn từ Combobox.
        """
        algo_name = self.cbo_algo.get()
        start_time = time.time()
        
        self.log_message(f"=== BẮT ĐẦU GIẢI PUZZLE BẰNG THUẬT TOÁN: {algo_name} ===")
        self.log_message(f"Trạng thái ban đầu: {self.trang_thai_dau}")
        self.log_message(f"Trạng thái Đích: {GOAL_STATE}")
        
        loi_giai = None
        dem_node = 0
        
        try:
            if "BFS" in algo_name:
                loi_giai, dem_node = BFS_Solver(self.trang_thai_dau, GOAL_STATE, self.log_message, self.check_stop_flag)
            elif "DFS" in algo_name:
                loi_giai, dem_node = DFS_Solver(self.trang_thai_dau, GOAL_STATE, 25, self.log_message, self.check_stop_flag)
            elif "UCS" in algo_name:
                loi_giai, dem_node = UCS_Solver(self.trang_thai_dau, GOAL_STATE, self.log_message, self.check_stop_flag)
            else: # IDS
                loi_giai, dem_node = IDS_Solver(self.trang_thai_dau, GOAL_STATE, self.log_message, self.check_stop_flag)
        except Exception as e:
            self.log_message(f"\n❌ Đã xảy ra lỗi trong quá trình tính toán: {str(e)}")
            
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Đưa lệnh cập nhật GUI trở lại luồng chính (Main Thread)
        self.root.after(0, self.on_solving_finished, loi_giai, dem_node, elapsed_time)

    def on_solving_finished(self, loi_giai, dem_node, elapsed_time):
        """
        Cập nhật lại giao diện ngay sau khi quá trình tìm kiếm lời giải kết thúc.
        """
        self.dang_chay_giai = False
        self.btn_solve.config(state=tk.NORMAL, text="▶ Chạy Giải")
        self.btn_shuffle.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        
        if self.flag_dung_giai:
            self.log_message("\n🛑 ĐÃ HỦY TÌM KIẾM THÀNH CÔNG THEO YÊU CẦU NGƯỜI DÙNG!")
            messagebox.showwarning("Hủy bỏ", "Quá trình tìm kiếm đã bị dừng ngang.")
            return

        if loi_giai:
            self.duong_di_loi_giai = loi_giai
            self.index_buoc_hien_tai = 0
            
            # Cập nhật bảng thống kê
            algo_name = self.cbo_algo.get()
            if "UCS" in algo_name:
                total_cost = sum(tinh_so_o_trung(s, GOAL_STATE) for s in loi_giai)
                self.lbl_stat_steps.config(text=f"• Số bước di chuyển: {len(loi_giai) - 1} bước (g(n) = {total_cost})")
            else:
                self.lbl_stat_steps.config(text=f"• Số bước di chuyển: {len(loi_giai) - 1} bước")
                
            self.lbl_stat_nodes.config(text=f"• Tổng số Node đã xét: {dem_node} nodes")
            self.lbl_stat_time.config(text=f"• Thời gian giải: {elapsed_time:.4f} giây")
            
            # Kích hoạt các nút trình diễn đường đi
            self.btn_prev.config(state=tk.DISABLED) # Đang ở bước 0 nên lùi bị disable
            self.btn_next.config(state=tk.NORMAL)
            self.btn_auto.config(state=tk.NORMAL)
            self.btn_reset.config(state=tk.NORMAL)
            
            self.log_message(f"\n✅ THÀNH CÔNG!")
            self.log_message(f"- Số bước trượt: {len(loi_giai) - 1}")
            if "UCS" in algo_name:
                self.log_message(f"- Tổng chi phí đường đi (Cost g(n)): {total_cost}")
            self.log_message(f"- Tổng số node đã duyệt qua: {dem_node}")
            self.log_message(f"- Thời gian giải thuật: {elapsed_time:.4f} giây")
            self.log_message("- Hãy nhấn 'Chạy Auto' hoặc nút 'Tiến' để mô phỏng đường đi về đích.")
            
            messagebox.showinfo("Thành công", f"Tìm thấy lời giải có độ dài {len(loi_giai) - 1} bước di chuyển!")
        else:
            self.log_message("\n❌ THẤT BẠI: Không tìm thấy bất kỳ lời giải nào!")
            messagebox.showerror("Thất bại", "Không thể tìm thấy đường đi đến đích trong giới hạn cho phép.")
            
        self.update_puzzle_grids()


# =============================================================================
# KHỞI CHẠY CHƯƠNG TRÌNH CHÍNH
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
