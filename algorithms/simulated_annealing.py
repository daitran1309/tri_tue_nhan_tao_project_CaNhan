# -*- coding: utf-8 -*-
from .utils import *
import random
import math

# Simulated Annealing - Giả lập luyện kim
def Simulated_Annealing_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    curr_node = tao_node(start_state, [start_state])
    dem_node = 1
    T = 100.0
    cooling_rate = 0.99

    while T > 0.1:
        if stop_flag and stop_flag():
            return None, dem_node
        curr_h = tinh_khoang_cach_manhattan(curr_node["state"], goal_state)
        if curr_h == 0:
            if log_callback:
                log_callback(f"[Simulated Annealing] TÌM THẤY LỜI GIẢI sau {dem_node} nodes!")
            return curr_node["duong_di"], dem_node

        children = EXPAND(curr_node)
        if not children:
            return None, dem_node
        next_node = random.choice(children)
        dem_node += 1

        next_h = tinh_khoang_cach_manhattan(next_node["state"], goal_state)
        delta_E = curr_h - next_h

        if delta_E > 0:
            curr_node = next_node
        else:
            prob = math.exp(delta_E / T)
            if random.random() < prob:
                curr_node = next_node

        T *= cooling_rate

    if log_callback:
        log_callback(f"[Simulated Annealing] Hết nhiệt độ mà chưa tới đích!")
    return None, dem_node
