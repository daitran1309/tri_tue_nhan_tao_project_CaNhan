# -*- coding: utf-8 -*-
"""
Các hàm tiện ích và hằng số dùng chung cho toàn bộ thuật toán 8-Puzzle.
"""
import heapq
from collections import deque
import random
import math
import time

# =============================================================================
# HẰNG SỐ HỆ THỐNG
# =============================================================================
GOAL_STATES = [
    [1, 2, 3,
     4, 5, 6,
     7, 8, 0],
    [1, 2, 3,
     8, 0, 4,
     7, 6, 5]
]
GOAL_STATE = GOAL_STATES[0]

CANDIDATE_GOALS = [
    [1, 2, 3,
     4, 5, 6,
     7, 8, 0],
    [1, 2, 3,
     8, 0, 4,
     7, 6, 5],
    [8, 7, 6,
     1, 0, 5,
     2, 3, 4]
]

# =============================================================================
# HÀM TIỆN ÍCH
# =============================================================================
def tao_node(state, duong_di, do_sau=0, cost=0):
    return {
        "state": state,
        "duong_di": duong_di,
        "do_sau": do_sau,
        "cost": cost
    }

def tinh_khoang_cach_manhattan(state, goal_state):
    """Tính tổng khoảng cách Manhattan từ các ô số đến vị trí đích."""
    distance = 0
    for i, val in enumerate(state):
        if val != 0:
            r_curr, c_curr = i // 3, i % 3
            idx_goal = goal_state.index(val)
            r_goal, c_goal = idx_goal // 3, idx_goal % 3
            distance += abs(r_curr - r_goal) + abs(c_curr - c_goal)
    return distance

def tinh_so_o_sai_khac(state, goal_state):
    """Tính số ô sai vị trí (không tính ô trống 0)."""
    return sum(1 for s, g in zip(state, goal_state) if s != 0 and s != g)

def EXPAND(node):
    """Mở rộng node bằng cách di chuyển ô trống theo 4 hướng."""
    state = node["state"]
    vi_tri_trong = state.index(0)
    hang = vi_tri_trong // 3
    cot  = vi_tri_trong % 3
    cac_con = []
    huong = [(hang - 1, cot), (hang + 1, cot), (hang, cot - 1), (hang, cot + 1)]
    for hang_moi, cot_moi in huong:
        if 0 <= hang_moi < 3 and 0 <= cot_moi < 3:
            vi_tri_moi = hang_moi * 3 + cot_moi
            state_moi = state.copy()
            state_moi[vi_tri_trong], state_moi[vi_tri_moi] = state_moi[vi_tri_moi], state_moi[vi_tri_trong]
            duong_di_moi = node["duong_di"] + [state_moi]
            child = tao_node(state_moi, duong_di_moi, node["do_sau"] + 1, node.get("cost", 0) + 1)
            cac_con.append(child)
    return cac_con

def sinh_de_ngau_nhien(goal_states, so_buoc=30):
    """Sinh đề ngẫu nhiên bằng cách trượt ngược từ đích, đảm bảo luôn giải được."""
    goal = random.choice(goal_states)
    state = goal.copy()
    vi_tri_cu = -1
    for _ in range(so_buoc):
        idx = state.index(0)
        hang = idx // 3
        cot = idx % 3
        nuoc_di_hop_le = []
        if hang > 0: nuoc_di_hop_le.append(idx - 3)
        if hang < 2: nuoc_di_hop_le.append(idx + 3)
        if cot > 0: nuoc_di_hop_le.append(idx - 1)
        if cot < 2: nuoc_di_hop_le.append(idx + 1)
        if vi_tri_cu in nuoc_di_hop_le and len(nuoc_di_hop_le) > 1:
            nuoc_di_hop_le.remove(vi_tri_cu)
        next_idx = random.choice(nuoc_di_hop_le)
        state[idx], state[next_idx] = state[next_idx], state[idx]
        vi_tri_cu = idx
    return state
