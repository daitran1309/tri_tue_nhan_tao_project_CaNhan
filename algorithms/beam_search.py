# -*- coding: utf-8 -*-
from .utils import *

# Beam Search - Tìm kiếm chùm tia (k = số beam giữ lại mỗi tầng)
def Beam_Search_Solver(start_state, goal_state, k=2, log_callback=None, stop_flag=None):
    node_dau = tao_node(start_state, [start_state])
    beam = [node_dau]
    dem_node = 1
    explored = {tuple(start_state)}

    while beam:
        if stop_flag and stop_flag():
            return None, dem_node
        next_beam = []
        for node in beam:
            if list(node["state"]) == goal_state:
                if log_callback:
                    log_callback(f"[Beam Search k={k}] TÌM THẤY LỜI GIẢI sau {dem_node} nodes!")
                return node["duong_di"], dem_node

            children = EXPAND(node)
            for child in children:
                child_tuple = tuple(child["state"])
                if child_tuple not in explored:
                    explored.add(child_tuple)
                    dem_node += 1
                    child["h"] = tinh_khoang_cach_manhattan(child["state"], goal_state)
                    next_beam.append(child)

        if not next_beam:
            break
        next_beam.sort(key=lambda x: x["h"])
        beam = next_beam[:k]

    if log_callback:
        log_callback(f"[Beam Search k={k}] Không tìm thấy lời giải (bị kẹt)!")
    return None, dem_node
