# -*- coding: utf-8 -*-
"""
=============================================================================
   THUẬT TOÁN UNIFORM COST SEARCH (UCS) CHO 8-PUZZLE
   Môn học: Trí tuệ nhân tạo
   Sinh viên thực hiện: Trần Phước Đại (MSSV: 24110190)
=============================================================================
   Đặc tả:
   1. Độ ưu tiên (priority): Số ô trùng với kết quả đích (h(n)).
   2. Chi phí (cost): Tổng số ô trùng lặp từ ô đầu tiên đến ô hiện tại (g(n)).
   3. Frontier: Sử dụng heapq để sắp xếp tăng dần theo cost g(n), 
      và sử dụng priority h(n) làm tie-breaker (ưu tiên node khớp nhiều hơn).
=============================================================================
"""

import heapq

def tinh_so_o_trung(state, goal_state):
    """
    Tính số lượng ô trùng khớp giữa trạng thái hiện tại và trạng thái đích.
    So sánh toàn bộ 9 vị trí (bao gồm cả ô trống 0).
    """
    return sum(1 for s, g in zip(state, goal_state) if s == g)

def tao_node_ucs(state, duong_di, do_sau, cost, priority):
    """
    Tạo cấu trúc Node lưu trữ trạng thái cho thuật toán UCS.
    """
    return {
        "state": state,        # Mảng 9 số biểu diễn trạng thái
        "duong_di": duong_di,  # Danh sách các state đi qua từ đầu đến node này
        "do_sau": do_sau,      # Độ sâu (số bước di chuyển)
        "cost": cost,          # g(n): Tổng số ô trùng từ start đến hiện tại
        "priority": priority   # h(n): Số ô trùng khớp của riêng state này
    }

def EXPAND_UCS(node, goal_state):
    """
    Mở rộng node hiện tại bằng cách di chuyển ô trống (0) sang 4 hướng,
    tính toán cost và priority tương ứng cho các node con.
    """
    state = node["state"]
    vi_tri_trong = state.index(0)
    hang = vi_tri_trong // 3
    cot  = vi_tri_trong % 3

    cac_con = []
    huong = [
        (hang - 1, cot),   # Lên
        (hang + 1, cot),   # Xuống
        (hang,     cot - 1),  # Trái
        (hang,     cot + 1),  # Phải
    ]

    for hang_moi, cot_moi in huong:
        if 0 <= hang_moi < 3 and 0 <= cot_moi < 3:
            vi_tri_moi = hang_moi * 3 + cot_moi
            
            # Tráo đổi ô trống
            state_moi = state.copy()
            state_moi[vi_tri_trong] = state_moi[vi_tri_moi]
            state_moi[vi_tri_moi] = 0
            
            duong_di_moi = node["duong_di"] + [state_moi]
            
            # Tính độ ưu tiên cho node con (số ô trùng của trạng thái mới)
            priority_moi = tinh_so_o_trung(state_moi, goal_state)
            
            # Chi phí mới = chi phí cha + độ ưu tiên mới (tổng số ô trùng lặp cả path)
            cost_moi = node["cost"] + priority_moi
            
            child = tao_node_ucs(state_moi, duong_di_moi, node["do_sau"] + 1, cost_moi, priority_moi)
            cac_con.append(child)

    return cac_con

def UCS_Solver(trang_thai_dau, trang_thai_dich, log_callback=None, stop_flag=None):
    """
    Giải trò chơi 8-puzzle bằng thuật toán Uniform Cost Search (UCS).
    - Frontier được sắp xếp theo g(n) = cost tăng dần.
    - Tie-breaker: Khi cost bằng nhau, ưu tiên node có h(n) = priority cao hơn (sắp xếp -priority).
    """
    # Khởi tạo node gốc
    p_dau = tinh_so_o_trung(trang_thai_dau, trang_thai_dich)
    node_dau = tao_node_ucs(trang_thai_dau, [trang_thai_dau], do_sau=0, cost=p_dau, priority=p_dau)
    
    if trang_thai_dau == trang_thai_dich:
        if log_callback:
            log_callback("[UCS] Trạng thái ban đầu đã trùng khớp với đích!")
        return node_dau["duong_di"], 1
        
    # Hàng đợi ưu tiên frontier. Định dạng lưu trữ: (cost, -priority, counter, node)
    # Vì heapq là min-heap nên -priority giúp lấy ra node có độ ưu tiên lớn nhất khi cost bằng nhau.
    counter = 0
    frontier = []
    heapq.heappush(frontier, (node_dau["cost"], -node_dau["priority"], counter, node_dau))
    
    explored = set()
    frontier_states = {tuple(trang_thai_dau)}
    
    dem_node = 0
    
    while frontier:
        # Kiểm tra dừng khẩn cấp từ GUI
        if stop_flag and stop_flag():
            return None, dem_node

        cost_val, neg_pri, _, node = heapq.heappop(frontier)
        state_tuple = tuple(node["state"])
        
        if state_tuple in explored:
            continue
            
        frontier_states.discard(state_tuple)
        explored.add(state_tuple)
        dem_node += 1
        
        # Ghi Trace Log lên GUI (Giới hạn hiển thị 100 node đầu để tránh lag)
        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: {node['state']} (g = {node['cost']} | h = {node['priority']})")
                log_callback(f"EXPLORED: {node['state']}")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu để tránh giật lag UI) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[UCS] Đang xét node thứ {dem_node}... (Frontier: {len(frontier)})")
                
        # Kiểm tra xem đã đạt trạng thái đích chưa
        if node["state"] == trang_thai_dich:
            if log_callback:
                log_callback(f"[UCS] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
            return node["duong_di"], dem_node
            
        # Mở rộng node con
        for child in EXPAND_UCS(node, trang_thai_dich):
            child_state = child["state"]
            child_tuple = tuple(child_state)
            
            if child_tuple not in explored and child_tuple not in frontier_states:
                if log_callback and dem_node <= 100:
                    log_callback(f"  PUSH FRONTIER: {child_state} (g = {child['cost']} | h = {child['priority']})")
                    
                counter += 1
                heapq.heappush(frontier, (child["cost"], -child["priority"], counter, child))
                frontier_states.add(child_tuple)
                
    return None, dem_node
