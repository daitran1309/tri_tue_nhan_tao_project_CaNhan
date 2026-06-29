# -*- coding: utf-8 -*-
from .utils import *

# DFS - Tìm kiếm theo chiều sâu (có giới hạn độ sâu)
def DFS_Solver(start_state, goal_state, limit=30, log_callback=None, stop_flag=None):
    node_dau = tao_node(start_state, [start_state])
    if list(start_state) == goal_state:
        return node_dau["duong_di"], 1
    frontier = [node_dau]
    explored = set()
    frontier_states = {tuple(start_state)}
    dem_node = 0
    while frontier:
        if stop_flag and stop_flag():
            return None, dem_node
        node = frontier.pop()
        curr_state = tuple(node["state"])
        frontier_states.discard(curr_state)
        explored.add(curr_state)
        dem_node += 1
        if log_callback and dem_node % 500 == 0:
            log_callback(f"[DFS] Đang xét node {dem_node}")

        if list(curr_state) == goal_state:
            return node["duong_di"], dem_node
        if node["do_sau"] < limit:
            for child in reversed(EXPAND(node)):
                child_state_tuple = tuple(child["state"])
                if child_state_tuple not in explored and child_state_tuple not in frontier_states:
                    if list(child_state_tuple) == goal_state:
                        if log_callback:
                            log_callback(f"[DFS] TÌM THẤY LỜI GIẢI sau {dem_node} nodes!")
                        return child["duong_di"], dem_node
                    frontier.append(child)
                    frontier_states.add(child_state_tuple)
    return None, dem_node
