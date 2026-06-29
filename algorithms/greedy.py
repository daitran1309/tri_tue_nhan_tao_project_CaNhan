# -*- coding: utf-8 -*-
from .utils import *
import heapq

# Greedy - Tìm kiếm tham lam (dùng heuristic Manhattan)
def Greedy_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    h_start = tinh_khoang_cach_manhattan(start_state, goal_state)
    node_dau = tao_node(start_state, [start_state])
    if list(start_state) == goal_state:
        return node_dau["duong_di"], 1
    counter = 0
    queue = [(h_start, counter, node_dau)]
    explored = set()
    frontier_states = {tuple(start_state): h_start}
    dem_node = 0
    while queue:
        if stop_flag and stop_flag():
            return None, dem_node
        h_val, _, node = heapq.heappop(queue)
        curr_state = tuple(node["state"])
        if curr_state in explored:
            continue
        explored.add(curr_state)
        dem_node += 1
        if log_callback and dem_node % 500 == 0:
            log_callback(f"[Greedy] Đang xét node {dem_node}")
        if list(curr_state) == goal_state:
            if log_callback:
                log_callback(f"[Greedy] TÌM THẤY LỜI GIẢI sau {dem_node} nodes!")
            return node["duong_di"], dem_node

        for child in EXPAND(node):
            child_state_tuple = tuple(child["state"])
            h_child = tinh_khoang_cach_manhattan(child["state"], goal_state)
            if child_state_tuple not in explored:
                if child_state_tuple not in frontier_states or h_child < frontier_states[child_state_tuple]:
                    frontier_states[child_state_tuple] = h_child
                    counter += 1
                    heapq.heappush(queue, (h_child, counter, child))
    return None, dem_node
