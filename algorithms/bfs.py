# -*- coding: utf-8 -*-
from .utils import *
from collections import deque

# BFS - Tìm kiếm theo chiều rộng
def BFS_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    node_dau = tao_node(start_state, [start_state])
    if list(start_state) == goal_state:
        return node_dau["duong_di"], 1
    frontier = deque([node_dau])
    explored = set()
    frontier_states = {tuple(start_state)}
    dem_node = 0
    while frontier:
        if stop_flag and stop_flag():
            return None, dem_node
        node = frontier.popleft()
        curr_state = tuple(node["state"])
        frontier_states.discard(curr_state)
        explored.add(curr_state)
        dem_node += 1
        if log_callback and dem_node % 500 == 0:
            log_callback(f"[BFS] Đang xét node {dem_node}")

        for child in EXPAND(node):
            child_state_tuple = tuple(child["state"])
            if child_state_tuple not in explored and child_state_tuple not in frontier_states:
                if list(child_state_tuple) == goal_state:
                    if log_callback:
                        log_callback(f"[BFS] TÌM THẤY LỜI GIẢI sau {dem_node} nodes!")
                    return child["duong_di"], dem_node
                frontier.append(child)
                frontier_states.add(child_state_tuple)
    return None, dem_node
