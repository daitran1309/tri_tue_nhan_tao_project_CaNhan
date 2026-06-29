from .utils import *
import random
import math
import heapq
from collections import deque

# 7. Leo đồi đơn giản
def Simple_Hill_Climbing_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    curr_node = tao_node(start_state, [start_state])
    dem_node = 1
    while True:
        if stop_flag and stop_flag(): return None, dem_node
        curr_h = tinh_khoang_cach_manhattan(curr_node["state"], goal_state)
        if curr_h == 0:
            if log_callback: log_callback(f"[Simple HC] TÌM THẤY LỜI GIẢI sau {dem_node} nodes!")
            return curr_node["duong_di"], dem_node
            
        children = EXPAND(curr_node)
        found_better = False
        for child in children:
            dem_node += 1
            child_h = tinh_khoang_cach_manhattan(child["state"], goal_state)
            if child_h < curr_h:
                curr_node = child
                found_better = True
                break
        
        if not found_better:
            if log_callback: log_callback(f"[Simple HC] Bị kẹt tại tối ưu cục bộ!")
            return None, dem_node

# 8. Leo đồi dốc nhất
def Steepest_Ascent_Hill_Climbing_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    curr_node = tao_node(start_state, [start_state])
    dem_node = 1
    while True:
        if stop_flag and stop_flag(): return None, dem_node
        curr_h = tinh_khoang_cach_manhattan(curr_node["state"], goal_state)
        if curr_h == 0:
            if log_callback: log_callback(f"[Steepest Ascent] TÌM THẤY LỜI GIẢI sau {dem_node} nodes!")
            return curr_node["duong_di"], dem_node
            
        children = EXPAND(curr_node)
        best_child = None
        best_h = curr_h
        for child in children:
            dem_node += 1
            child_h = tinh_khoang_cach_manhattan(child["state"], goal_state)
            if child_h < best_h:
                best_child = child
                best_h = child_h
                
        if best_child is None:
            if log_callback: log_callback(f"[Steepest Ascent] Bị kẹt tại tối ưu cục bộ!")
            return None, dem_node
        curr_node = best_child
