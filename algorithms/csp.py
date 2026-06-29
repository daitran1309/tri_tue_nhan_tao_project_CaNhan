# -*- coding: utf-8 -*-
import random

# =============================================================================
# THUẬT TOÁN CSP CHO 8-PUZZLE
# Mô hình hóa: 9 biến (vị trí 0-8), mỗi biến gán giá trị là số (0-8)
# Ràng buộc: AllDiff + phải khớp với trạng thái đích
# =============================================================================

def CSP_Backtracking_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    """CSP Backtracking: Gán lần lượt giá trị cho từng ô, quay lui khi vi phạm."""
    duong_di = []
    state = [None] * 9
    dem_node = [0]

    def backtrack(p):
        if stop_flag and stop_flag():
            return False
        if p == 9:
            return True

        for t in range(9):
            if stop_flag and stop_flag():
                return False
            dem_node[0] += 1
            state[p] = t
            duong_di.append(state.copy())

            if t in state[:p]:
                continue
            if t != goal_state[p]:
                continue

            if backtrack(p + 1):
                return True

        state[p] = None
        duong_di.append(state.copy())
        return False

    backtrack(0)
    return duong_di, dem_node[0]


def CSP_Forward_Checking_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    """CSP Forward Checking: Giống Backtracking nhưng loại trước các giá trị vi phạm."""
    duong_di = []
    state = [None] * 9
    dem_node = [0]
    domains = {p: list(range(9)) for p in range(9)}

    def fc(p):
        if stop_flag and stop_flag():
            return False
        if p == 9:
            return True

        for t in list(domains[p]):
            if stop_flag and stop_flag():
                return False
            dem_node[0] += 1
            state[p] = t
            duong_di.append(state.copy())

            if t != goal_state[p]:
                continue

            domains_backup = {k: v.copy() for k, v in domains.items()}
            empty_domain_found = False
            for next_p in range(p + 1, 9):
                if t in domains[next_p]:
                    domains[next_p].remove(t)
                if not domains[next_p]:
                    empty_domain_found = True
                    break

            if not empty_domain_found:
                if fc(p + 1):
                    return True

            domains.update(domains_backup)

        state[p] = None
        duong_di.append(state.copy())
        return False

    fc(0)
    return duong_di, dem_node[0]


def CSP_Min_Conflicts_Solver(start_state, goal_state, log_callback=None, stop_flag=None):
    """CSP Min-Conflicts: Khởi tạo ngẫu nhiên, hoán đổi để giảm xung đột."""
    duong_di = []
    state = list(start_state)
    duong_di.append(state.copy())
    dem_node = 0

    for _ in range(100):
        if stop_flag and stop_flag():
            return None, dem_node

        conflicts = [i for i in range(9) if state[i] != goal_state[i]]
        if not conflicts:
            return duong_di, dem_node

        var = random.choice(conflicts)
        correct_val = goal_state[var]
        swap_idx = state.index(correct_val)

        dem_node += 1
        state[var], state[swap_idx] = state[swap_idx], state[var]
        duong_di.append(state.copy())

    return duong_di, dem_node
