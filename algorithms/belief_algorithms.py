# -*- coding: utf-8 -*-
"""
Các thuật toán tìm kiếm Belief State (2 trạng thái đồng thời)
cho bài toán 8-Puzzle trong môi trường mù hoàn toàn và nhìn thấy 1 phần.
"""
import heapq
from collections import deque
import random
from .utils import GOAL_STATES, CANDIDATE_GOALS, tinh_khoang_cach_manhattan


# =============================================================================
# HÀM HỖ TRỢ CHO BELIEF STATE
# =============================================================================
def apply_action_conformant(state, action):
    """
    Áp dụng hành động (UP, DOWN, LEFT, RIGHT) lên trạng thái state.
    Nếu hợp lệ: trả về trạng thái mới. Nếu không: trả về trạng thái cũ.
    """
    idx = state.index(0)
    r, c = idx // 3, idx % 3
    if action == "UP" and r > 0:
        new_idx = idx - 3
    elif action == "DOWN" and r < 2:
        new_idx = idx + 3
    elif action == "LEFT" and c > 0:
        new_idx = idx - 1
    elif action == "RIGHT" and c < 2:
        new_idx = idx + 1
    else:
        return state
    new_state = state.copy()
    new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
    return new_state


def expand_belief(node):
    """Mở rộng node niềm tin (2 trạng thái A, B) theo 4 hướng."""
    curr_belief = node["state"]
    state_A, state_B = curr_belief
    actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    children = []

    for action in actions:
        new_state_A = apply_action_conformant(list(state_A), action)
        new_state_B = apply_action_conformant(list(state_B), action)

        if new_state_A == list(state_A) and new_state_B == list(state_B):
            continue

        child_state = (tuple(new_state_A), tuple(new_state_B))
        duong_di_moi = node["duong_di"] + [child_state]
        child_node = {
            "state": child_state,
            "duong_di": duong_di_moi,
            "do_sau": node["do_sau"] + 1
        }
        children.append(child_node)

    return children


def canonical_belief(state_tuple):
    """Chuẩn hóa trạng thái niềm tin (không phân biệt thứ tự A, B)."""
    return tuple(sorted(state_tuple))


# =============================================================================
# BFS Belief State
# =============================================================================
def BFS_Belief_Solver(trang_thai_dau_A, trang_thai_dau_B, log_callback=None, stop_flag=None):
    node_dau = {
        "state": (tuple(trang_thai_dau_A), tuple(trang_thai_dau_B)),
        "duong_di": [(trang_thai_dau_A.copy(), trang_thai_dau_B.copy())],
        "do_sau": 0
    }

    if list(node_dau["state"][0]) in GOAL_STATES and list(node_dau["state"][1]) in GOAL_STATES:
        return node_dau["duong_di"], 1

    frontier = deque([node_dau])
    explored = set()
    frontier_states = {canonical_belief(node_dau["state"])}
    dem_node = 0

    while frontier:
        if stop_flag and stop_flag():
            return None, dem_node
        node = frontier.popleft()
        curr_belief = node["state"]
        canonical_curr = canonical_belief(curr_belief)
        frontier_states.discard(canonical_curr)
        explored.add(canonical_curr)
        dem_node += 1

        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: A:{list(curr_belief[0])} | B:{list(curr_belief[1])}")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[BFS] Đang xét node thứ {dem_node}... (Frontier: {len(frontier)})")

        children = expand_belief(node)
        for child in children:
            child_state = child["state"]
            canonical_child = canonical_belief(child_state)
            if canonical_child not in explored and canonical_child not in frontier_states:
                if log_callback and dem_node <= 100:
                    log_callback(f"  PUSH FRONTIER: A:{list(child_state[0])} | B:{list(child_state[1])}")
                if list(child_state[0]) in GOAL_STATES and list(child_state[1]) in GOAL_STATES:
                    if log_callback:
                        log_callback(f"[BFS] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
                    return child["duong_di"], dem_node
                frontier.append(child)
                frontier_states.add(canonical_child)

    return None, dem_node


# =============================================================================
# DFS Belief State
# =============================================================================
def DFS_Belief_Solver(trang_thai_dau_A, trang_thai_dau_B, gioi_han_do_sau=25, log_callback=None, stop_flag=None):
    node_dau = {
        "state": (tuple(trang_thai_dau_A), tuple(trang_thai_dau_B)),
        "duong_di": [(trang_thai_dau_A.copy(), trang_thai_dau_B.copy())],
        "do_sau": 0
    }

    if list(node_dau["state"][0]) in GOAL_STATES and list(node_dau["state"][1]) in GOAL_STATES:
        return node_dau["duong_di"], 1

    frontier = [node_dau]
    explored = set()
    frontier_states = {canonical_belief(node_dau["state"])}
    dem_node = 0

    while frontier:
        if stop_flag and stop_flag():
            return None, dem_node
        node = frontier.pop()
        curr_belief = node["state"]
        canonical_curr = canonical_belief(curr_belief)
        frontier_states.discard(canonical_curr)
        explored.add(canonical_curr)
        dem_node += 1

        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: A:{list(curr_belief[0])} | B:{list(curr_belief[1])} (d = {node['do_sau']})")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[DFS] Đang xét node thứ {dem_node} ở độ sâu d = {node['do_sau']}...")

        if list(curr_belief[0]) in GOAL_STATES and list(curr_belief[1]) in GOAL_STATES:
            if log_callback:
                log_callback(f"[DFS] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
            return node["duong_di"], dem_node

        if node["do_sau"] >= gioi_han_do_sau:
            continue

        children = expand_belief(node)
        for child in reversed(children):
            child_state = child["state"]
            canonical_child = canonical_belief(child_state)
            if canonical_child not in explored and canonical_child not in frontier_states:
                if log_callback and dem_node <= 100:
                    log_callback(f"  PUSH FRONTIER: A:{list(child_state[0])} | B:{list(child_state[1])}")
                if list(child_state[0]) in GOAL_STATES and list(child_state[1]) in GOAL_STATES:
                    if log_callback:
                        log_callback(f"[DFS] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
                    return child["duong_di"], dem_node
                frontier.append(child)
                frontier_states.add(canonical_child)

    return None, dem_node


# =============================================================================
# DLS & IDS Belief State
# =============================================================================
def DLS_Belief_Solver(trang_thai_dau_A, trang_thai_dau_B, limit, visited_depth, log_callback=None, stop_flag=None, count_nodes_ref=None):
    node_dau = {
        "state": (tuple(trang_thai_dau_A), tuple(trang_thai_dau_B)),
        "duong_di": [(trang_thai_dau_A.copy(), trang_thai_dau_B.copy())],
        "do_sau": 0
    }

    if list(node_dau["state"][0]) in GOAL_STATES and list(node_dau["state"][1]) in GOAL_STATES:
        return node_dau["duong_di"]

    frontier = [(node_dau, {canonical_belief(node_dau["state"])})]

    while frontier:
        if stop_flag and stop_flag():
            return None
        node, path_set = frontier.pop()
        curr_state = node["state"]
        canonical_curr = canonical_belief(curr_state)

        if canonical_curr in visited_depth and visited_depth[canonical_curr] <= node["do_sau"]:
            continue
        visited_depth[canonical_curr] = node["do_sau"]

        if count_nodes_ref is not None:
            count_nodes_ref[0] += 1

        if log_callback and count_nodes_ref is not None and count_nodes_ref[0] <= 100:
            log_callback(f"[DLS d={limit}] POP: A:{list(curr_state[0])} | B:{list(curr_state[1])} (d={node['do_sau']})")

        if list(curr_state[0]) in GOAL_STATES and list(curr_state[1]) in GOAL_STATES:
            return node["duong_di"]

        if node["do_sau"] < limit:
            children = expand_belief(node)
            for child in reversed(children):
                child_state = child["state"]
                canonical_child = canonical_belief(child_state)
                if canonical_child not in path_set:
                    if canonical_child in visited_depth and visited_depth[canonical_child] <= child["do_sau"]:
                        continue
                    if list(child_state[0]) in GOAL_STATES and list(child_state[1]) in GOAL_STATES:
                        return child["duong_di"]
                    new_path_set = path_set.copy()
                    new_path_set.add(canonical_child)
                    frontier.append((child, new_path_set))

    return None


def IDS_Belief_Solver(trang_thai_dau_A, trang_thai_dau_B, log_callback=None, stop_flag=None):
    dem_node = [0]
    max_depth = 50
    for depth in range(max_depth + 1):
        if stop_flag and stop_flag():
            return None, dem_node[0]
        if log_callback:
            log_callback(f"\n--- BẮT ĐẦU DLS VỚI GIỚI HẠN ĐỘ SÂU = {depth} ---")
        visited_depth = {}
        loi_giai = DLS_Belief_Solver(
            trang_thai_dau_A, trang_thai_dau_B, depth, visited_depth,
            log_callback=log_callback, stop_flag=stop_flag, count_nodes_ref=dem_node
        )
        if loi_giai is not None:
            if log_callback:
                log_callback(f"[IDS] TÌM THẤY LỜI GIẢI ở giới hạn độ sâu d = {depth} sau khi duyệt {dem_node[0]} nodes!")
            return loi_giai, dem_node[0]
    return None, dem_node[0]


# =============================================================================
# Đoán đích (Goal Guessing)
# =============================================================================
def guess_goal(known_indices, active_goal):
    for goal in CANDIDATE_GOALS:
        if all(goal[i] == active_goal[i] for i in known_indices):
            return goal
    return active_goal


# =============================================================================
# UCS Belief State
# =============================================================================
def UCS_Belief_Solver(trang_thai_dau_A, trang_thai_dau_B, target_goal, log_callback=None, stop_flag=None):
    node_dau = {
        "state": (tuple(trang_thai_dau_A), tuple(trang_thai_dau_B)),
        "duong_di": [(trang_thai_dau_A.copy(), trang_thai_dau_B.copy())],
        "do_sau": 0, "g": 0
    }
    if list(node_dau["state"][0]) == target_goal and list(node_dau["state"][1]) == target_goal:
        return node_dau["duong_di"], 1

    counter = 0
    queue = [(0, counter, node_dau)]
    explored = set()
    frontier_states = {canonical_belief(node_dau["state"]): 0}
    dem_node = 0

    while queue:
        if stop_flag and stop_flag():
            return None, dem_node
        g_val, _, node = heapq.heappop(queue)
        curr_belief = node["state"]
        canonical_curr = canonical_belief(curr_belief)
        if canonical_curr in explored:
            continue
        explored.add(canonical_curr)
        dem_node += 1

        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: A:{list(curr_belief[0])} | B:{list(curr_belief[1])} (g={g_val})")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[UCS] Đang xét node thứ {dem_node}... (Queue: {len(queue)})")

        children = expand_belief(node)
        for child in children:
            child_state = child["state"]
            canonical_child = canonical_belief(child_state)
            g_child = g_val + 1
            child["g"] = g_child
            if canonical_child not in explored:
                if canonical_child not in frontier_states or g_child < frontier_states[canonical_child]:
                    frontier_states[canonical_child] = g_child
                    if log_callback and dem_node <= 100:
                        log_callback(f"  PUSH: A:{list(child_state[0])} | B:{list(child_state[1])} (g={g_child})")
                    if list(child_state[0]) == target_goal and list(child_state[1]) == target_goal:
                        if log_callback:
                            log_callback(f"[UCS] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
                        return child["duong_di"], dem_node
                    counter += 1
                    heapq.heappush(queue, (g_child, counter, child))

    return None, dem_node


# =============================================================================
# Greedy Belief State
# =============================================================================
def Greedy_Belief_Solver(trang_thai_dau_A, trang_thai_dau_B, target_goal, log_callback=None, stop_flag=None):
    h_start = tinh_khoang_cach_manhattan(trang_thai_dau_A, target_goal) + tinh_khoang_cach_manhattan(trang_thai_dau_B, target_goal)
    node_dau = {
        "state": (tuple(trang_thai_dau_A), tuple(trang_thai_dau_B)),
        "duong_di": [(trang_thai_dau_A.copy(), trang_thai_dau_B.copy())],
        "do_sau": 0, "h": h_start
    }
    if list(node_dau["state"][0]) == target_goal and list(node_dau["state"][1]) == target_goal:
        return node_dau["duong_di"], 1

    counter = 0
    queue = [(h_start, counter, node_dau)]
    explored = set()
    frontier_states = {canonical_belief(node_dau["state"]): h_start}
    dem_node = 0

    while queue:
        if stop_flag and stop_flag():
            return None, dem_node
        h_val, _, node = heapq.heappop(queue)
        curr_belief = node["state"]
        canonical_curr = canonical_belief(curr_belief)
        if canonical_curr in explored:
            continue
        explored.add(canonical_curr)
        dem_node += 1

        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: A:{list(curr_belief[0])} | B:{list(curr_belief[1])} (h={h_val})")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[Greedy] Đang xét node thứ {dem_node}... (Queue: {len(queue)})")

        children = expand_belief(node)
        for child in children:
            child_state = child["state"]
            canonical_child = canonical_belief(child_state)
            h_child = tinh_khoang_cach_manhattan(list(child_state[0]), target_goal) + tinh_khoang_cach_manhattan(list(child_state[1]), target_goal)
            child["h"] = h_child
            if canonical_child not in explored:
                if canonical_child not in frontier_states or h_child < frontier_states[canonical_child]:
                    frontier_states[canonical_child] = h_child
                    if log_callback and dem_node <= 100:
                        log_callback(f"  PUSH: A:{list(child_state[0])} | B:{list(child_state[1])} (h={h_child})")
                    if list(child_state[0]) == target_goal and list(child_state[1]) == target_goal:
                        if log_callback:
                            log_callback(f"[Greedy] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
                        return child["duong_di"], dem_node
                    counter += 1
                    heapq.heappush(queue, (h_child, counter, child))

    return None, dem_node


# =============================================================================
# A* Belief State
# =============================================================================
def AStar_Belief_Solver(trang_thai_dau_A, trang_thai_dau_B, target_goal, log_callback=None, stop_flag=None):
    h_start = tinh_khoang_cach_manhattan(trang_thai_dau_A, target_goal) + tinh_khoang_cach_manhattan(trang_thai_dau_B, target_goal)
    node_dau = {
        "state": (tuple(trang_thai_dau_A), tuple(trang_thai_dau_B)),
        "duong_di": [(trang_thai_dau_A.copy(), trang_thai_dau_B.copy())],
        "do_sau": 0, "g": 0, "h": h_start, "f": h_start
    }
    if list(node_dau["state"][0]) == target_goal and list(node_dau["state"][1]) == target_goal:
        return node_dau["duong_di"], 1

    counter = 0
    queue = [(h_start, counter, node_dau)]
    explored = set()
    frontier_states = {canonical_belief(node_dau["state"]): h_start}
    dem_node = 0

    while queue:
        if stop_flag and stop_flag():
            return None, dem_node
        f_val, _, node = heapq.heappop(queue)
        curr_belief = node["state"]
        canonical_curr = canonical_belief(curr_belief)
        if canonical_curr in explored:
            continue
        explored.add(canonical_curr)
        dem_node += 1

        if log_callback:
            if dem_node <= 100:
                log_callback(f"POP: A:{list(curr_belief[0])} | B:{list(curr_belief[1])} (f={f_val})")
            elif dem_node == 101:
                log_callback("... (Đạt giới hạn hiển thị chi tiết 100 nodes đầu) ...")
            elif dem_node % 100 == 0:
                log_callback(f"[A*] Đang xét node thứ {dem_node}... (Queue: {len(queue)})")

        children = expand_belief(node)
        for child in children:
            child_state = child["state"]
            canonical_child = canonical_belief(child_state)
            g_child = node["g"] + 1
            h_child = tinh_khoang_cach_manhattan(list(child_state[0]), target_goal) + tinh_khoang_cach_manhattan(list(child_state[1]), target_goal)
            f_child = g_child + h_child
            child["g"] = g_child
            child["h"] = h_child
            child["f"] = f_child
            if canonical_child not in explored:
                if canonical_child not in frontier_states or f_child < frontier_states[canonical_child]:
                    frontier_states[canonical_child] = f_child
                    if log_callback and dem_node <= 100:
                        log_callback(f"  PUSH: A:{list(child_state[0])} | B:{list(child_state[1])} (f={f_child})")
                    if list(child_state[0]) == target_goal and list(child_state[1]) == target_goal:
                        if log_callback:
                            log_callback(f"[A*] TÌM THẤY LỜI GIẢI sau khi xét {dem_node} nodes!")
                        return child["duong_di"], dem_node
                    counter += 1
                    heapq.heappush(queue, (f_child, counter, child))

    return None, dem_node
