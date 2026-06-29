# -*- coding: utf-8 -*-
from .utils import *

# DLS - Tìm kiếm theo chiều sâu có giới hạn (helper cho IDS)
def DLS(start_state, goal_state, limit, dem_node_ref, log_callback, stop_flag):
    node_dau = tao_node(start_state, [start_state])
    if list(start_state) == goal_state:
        return node_dau["duong_di"]
    frontier = [node_dau]
    visited_depth = {tuple(start_state): 0}
    while frontier:
        if stop_flag and stop_flag():
            return None
        node = frontier.pop()
        dem_node_ref[0] += 1
        curr_state = tuple(node["state"])
        if list(curr_state) == goal_state:
            return node["duong_di"]
        if node["do_sau"] < limit:
            for child in reversed(EXPAND(node)):
                child_state_tuple = tuple(child["state"])
                if child_state_tuple not in visited_depth or visited_depth[child_state_tuple] > child["do_sau"]:
                    visited_depth[child_state_tuple] = child["do_sau"]
                    if list(child_state_tuple) == goal_state:
                        return child["duong_di"]
                    frontier.append(child)
    return None

# IDS - Tìm kiếm sâu dần (Iterative Deepening Search)
def IDS_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    dem_node_ref = [0]
    for depth in range(50):
        if stop_flag and stop_flag():
            return None, dem_node_ref[0]
        if log_callback:
            log_callback(f"[IDS] Đang duyệt độ sâu = {depth}")
        res = DLS(start_state, goal_state, depth, dem_node_ref, log_callback, stop_flag)
        if res:
            if log_callback:
                log_callback(f"[IDS] TÌM THẤY LỜI GIẢI sau {dem_node_ref[0]} nodes!")
            return res, dem_node_ref[0]
    return None, dem_node_ref[0]
