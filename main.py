# -*- coding: utf-8 -*-
"""
=============================================================================
   CHƯƠNG TRÌNH GIẢI TRÒ CHƠI 8-PUZZLE TRỰC QUAN (GUI TKINTER)
   Môn học: Trí tuệ nhân tạo
   Sinh viên thực hiện: Trần Phước Đại (MSSV: 24110190)
=============================================================================
   Các tính năng chính:
   1. Giao diện trực quan hiện đại: Trạng thái đầu, Trạng thái đích và Puzzle hiện tại.
   2. Bộ sinh đề ngẫu nhiên (Shuffle): Luôn đảm bảo giải được (Solvable).
   3. Tích hợp thuật toán Beam Search (Tìm kiếm chùm tia).
   4. Trình diễn đường đi kết quả: Cho phép di chuyển từng bước (Lùi/Tiến) hoặc
      chạy tự động (Auto Play) với thanh điều chỉnh tốc độ mượt mà.
   5. Chạy đa luồng (Threading): Giúp giao diện không bị treo khi giải.
   6. Bảng nhật ký Trace Log & Thống kê sinh động trực quan.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
import re
import math
from collections import deque
import heapq
from algorithms import *

# =============================================================================
# CẤU HÌNH & HẰNG SỐ (được import từ algorithms/utils.py)
# =============================================================================

# Màu sắc giao diện (Premium Palette)
COLOR_BG = "#F8F9FA"          # Màu nền sáng, hiện đại
COLOR_CARD = "#FFFFFF"        # Màu nền của các ô số (trắng tinh)
COLOR_EMPTY = "#E9ECEF"       # Màu nền ô trống (0) - xám nhạt
COLOR_TEXT_MAIN = "#212529"   # Màu chữ số chính - đen đậm
COLOR_ACCENT = "#495057"      # Màu xám tiêu đề
COLOR_SUCCESS = "#28A745"     # Màu xanh lá khi thành công
COLOR_BTN_PRIMARY = "#E2E6EA" # Màu nút chức năng mặc định
COLOR_BTN_ACTIVE = "#DAE0E5"  # Màu nút khi rê chuột qua
COLOR_HIGHLIGHT = "#FFC107"   # Vàng nhẹ làm nổi bật

def add_hover_effect(widget, default_bg, hover_bg, default_fg=None, hover_fg=None):
    def on_enter(e):
        if str(widget.cget('state')) != tk.DISABLED:
            widget['background'] = hover_bg
            if hover_fg: widget['foreground'] = hover_fg
    def on_leave(e):
        if str(widget.cget('state')) != tk.DISABLED:
            widget['background'] = default_bg
            if default_fg: widget['foreground'] = default_fg
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Trực quan - Trần Phước Đại (24110190)")
        # Tự động phóng to toàn màn hình khi khởi chạy
        self.root.state('zoomed')
        self.root.configure(bg=COLOR_BG)

        # Biến trạng thái của ứng dụng
        self.trang_thai_dau_A = [1, 2, 3, 4, 0, 6, 7, 5, 8]
        self.trang_thai_dau_B = [0, 2, 3, 1, 8, 4, 7, 6, 5]
        self.duong_di_loi_giai = []
        self.index_buoc_hien_tai = 0
        self.dang_chay_giai = False
        self.dang_chay_auto = False
        self.flag_dung_giai = False
        self.is_animating = False

        # Các biến dùng cho môi trường nhìn thấy 1 phần
        self.active_goal_index = 0
        self.known_indices = [0, 1, 2]  # 3 ô nhìn thấy mặc định

        # Thiết kế giao diện chính
        self.setup_styles()
        self.build_gui()

        # Cập nhật hiển thị giao diện theo thuật toán đang chọn
        self.on_algo_changed(None)

        # Hiển thị trạng thái ban đầu lên bảng
        self.update_puzzle_grids()

    def setup_styles(self):
        """
        Cài đặt các style hiện đại cho các widget Tkinter.
        """
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Cấu hình màu nền cho Combobox và Button
        self.style.configure("TCombobox", fieldbackground="white", background=COLOR_BTN_PRIMARY, font=("Segoe UI", 11))
        self.style.configure("TButton", font=("Segoe UI", 11), background=COLOR_BTN_PRIMARY, borderwidth=1)
        self.style.map("TButton", background=[("active", COLOR_BTN_ACTIVE)])

    def build_gui(self):
        """
        Xây dựng cấu trúc layout của chương trình.
        """
        # --- TIÊU ĐỀ CHƯƠNG TRÌNH ---
        title_frame = tk.Frame(self.root, bg=COLOR_BG, pady=5)
        title_frame.pack(fill=tk.X)

        lbl_title = tk.Label(title_frame, text="CHƯƠNG TRÌNH GIẢI 8-PUZZLE TRỰC QUAN",
                             font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BG)
                             # Giảm font tiêu đề từ 20 xuống 16 để gom gọn kích thước
        lbl_title.pack()

        lbl_sub = tk.Label(title_frame, text="Học viên: Trần Phước Đại - MSSV: 24110190 - Lớp Trí tuệ nhân tạo",
                            font=("Segoe UI", 9, "italic"), fg=COLOR_ACCENT, bg=COLOR_BG)
        lbl_sub.pack()

        # --- KHUNG NỘI DUNG CHÍNH (Chi tay đôi: Trái & Phải) ---
        main_container = tk.Frame(self.root, bg=COLOR_BG, padx=15, pady=5)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Cột Trái: Bảng game & Các nút điều khiển
        left_col = tk.Frame(main_container, bg=COLOR_BG)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Cột Phải: Nhật ký Trace log & Bảng thống kê (Tăng chiều rộng lên 430px để hiển thị log chi tiết rộng hơn)
        right_col = tk.Frame(main_container, bg=COLOR_BG, width=430)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(15, 0))
        right_col.pack_propagate(False)

        # =====================================================================
        # THIẾT KẾ CỘT TRÁI (GAMEPLAY & CONTROLS)
        # =====================================================================
        # Khung chứa 2 bảng phía trên: Bảng Trạng thái đầu & Bảng Đích
        top_grids_frame = tk.Frame(left_col, bg=COLOR_BG)
        top_grids_frame.pack(fill=tk.X, pady=(0, 5))

        # 1. Bảng Trạng thái đầu (Gồm A và B)
        self.frame_start = tk.LabelFrame(top_grids_frame, text=" Trạng thái ban đầu (A & B) ",
                                    font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=8, pady=5)
        self.frame_start.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Trạng thái A
        self.frame_start_A = tk.LabelFrame(self.frame_start, text=" Trạng thái A ",
                                      font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=5, pady=2)
        self.frame_start_A.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
        self.start_tiles_A = []
        self.board_start_A = self.create_puzzle_grid_ui(self.frame_start_A, self.start_tiles_A, self.trang_thai_dau_A)

        # Trạng thái B
        self.frame_start_B = tk.LabelFrame(self.frame_start, text=" Trạng thái B ",
                                      font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=5, pady=2)
        self.frame_start_B.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.start_tiles_B = []
        self.board_start_B = self.create_puzzle_grid_ui(self.frame_start_B, self.start_tiles_B, self.trang_thai_dau_B)

        # Nút Shuffle đặt ở cuối frame_start
        self.btn_shuffle = tk.Button(self.frame_start, text="🔄 Shuffle (Sinh đề ngẫu nhiên)",
                                      font=("Segoe UI", 9, "bold"), bg="#E1DFDA", fg="#333", relief="flat",
                                      padx=8, pady=2, command=self.handle_shuffle)
        self.btn_shuffle.pack(side=tk.BOTTOM, pady=(5, 0))
        add_hover_effect(self.btn_shuffle, "#E1DFDA", "#D0CCC3")

        # Khung mũi tên chuyển đổi ở giữa (Giảm font từ 36 xuống 24)
        arrow_frame = tk.Frame(top_grids_frame, bg=COLOR_BG)
        arrow_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        lbl_arrow = tk.Label(arrow_frame, text="➔", font=("Segoe UI", 24), fg=COLOR_ACCENT, bg=COLOR_BG)
        lbl_arrow.pack(expand=True)

        # 2. Bảng Đích (Gồm Đích 1, Đích 2 và Đích nhìn thấy 1 phần)
        self.frame_goal = tk.LabelFrame(top_grids_frame, text=" Trạng thái Đích (1 trong 2) ",
                                   font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=8, pady=5)
        self.frame_goal.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Đích 1
        self.frame_goal_1 = tk.LabelFrame(self.frame_goal, text=" Đích 1 ",
                                     font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=5, pady=2)
        self.frame_goal_1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
        self.goal_tiles_1 = []
        self.board_goal_1 = self.create_puzzle_grid_ui(self.frame_goal_1, self.goal_tiles_1, GOAL_STATES[0])

        # Đích 2
        self.frame_goal_2 = tk.LabelFrame(self.frame_goal, text=" Đích 2 ",
                                     font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=5, pady=2)
        self.frame_goal_2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.goal_tiles_2 = []
        self.board_goal_2 = self.create_puzzle_grid_ui(self.frame_goal_2, self.goal_tiles_2, GOAL_STATES[1])

        # Đích nhìn thấy 1 phần (Mặc định ẩn, sẽ pack trong on_algo_changed)
        self.frame_goal_partial = tk.LabelFrame(self.frame_goal, text=" Đích thực tế (Chỉ biết vài ô) ",
                                                font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=5, pady=2)
        self.goal_tiles_partial = []
        self.create_puzzle_grid_ui(self.frame_goal_partial, self.goal_tiles_partial, CANDIDATE_GOALS[0])

        # 3. Khung bảng điều khiển thuật toán ở giữa
        control_panel = tk.LabelFrame(left_col, text=" Bảng điều khiển giải thuật ",
                                      font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=12, pady=6)
        control_panel.pack(fill=tk.X, pady=5)

        # Combobox chọn thuật toán
        tk.Label(control_panel, text="Chọn thuật toán:", font=("Segoe UI", 10), bg=COLOR_BG).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.cbo_algo = ttk.Combobox(control_panel, values=[
            "BFS", "DFS", "IDS", "UCS", "A*",
            "Leo đồi đơn giản", "Leo đồi dốc nhất", "Greedy", "Giả lập luyện kim", "Beam search k=2",
            "CSP Backtracking", "CSP Forward Checking", "CSP Min-Conflicts",
            "BFS (Initial Belief State)",
            "DFS (Initial Belief State)",
            "IDS (Initial Belief State)",
            "UCS (Môi trường nhìn thấy 1 phần)",
            "Greedy (Môi trường nhìn thấy 1 phần)",
            "A* (Môi trường nhìn thấy 1 phần)"
        ], state="readonly", width=30)
        self.cbo_algo.grid(row=0, column=1, padx=5, pady=3)
        self.cbo_algo.current(0) # Chọn mặc định là BFS (Initial Belief State)
        self.cbo_algo.bind("<<ComboboxSelected>>", self.on_algo_changed)

        # Nút Chạy giải thuật
        self.btn_solve = tk.Button(control_panel, text="▶ Chạy Giải", font=("Segoe UI", 10, "bold"),
                                   bg="#4CAF50", fg="white", activebackground="#43A047", relief="flat", padx=10,
                                   command=self.start_solving_thread)
        self.btn_solve.grid(row=0, column=2, padx=10, pady=3)
        add_hover_effect(self.btn_solve, "#4CAF50", "#45a049")

        # Nút Dừng khẩn cấp
        self.btn_stop = tk.Button(control_panel, text="⏹ Dừng", font=("Segoe UI", 10, "bold"),
                                  bg="#F44336", fg="white", activebackground="#E53935", relief="flat", padx=10,
                                  state=tk.DISABLED, command=self.stop_solving)
        self.btn_stop.grid(row=0, column=3, padx=5, pady=3)
        add_hover_effect(self.btn_stop, "#F44336", "#e53935")

        # Ngăn cách giữa hai nhóm nút (Giảm pady dọc xuống 6)
        separator = ttk.Separator(control_panel, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=5, sticky="ew", pady=6)

        # Dòng nút điều khiển kết quả: Lùi, Tiến, Auto, Reset
        result_buttons_frame = tk.Frame(control_panel, bg=COLOR_BG)
        result_buttons_frame.grid(row=2, column=0, columnspan=5, sticky="ew")

        self.btn_prev = tk.Button(result_buttons_frame, text="◀ Bước Lùi", font=("Segoe UI", 9), bg="#E1DFDA", relief="flat", padx=8, command=self.step_prev, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=3)
        add_hover_effect(self.btn_prev, "#E1DFDA", "#D0CCC3")

        self.btn_next = tk.Button(result_buttons_frame, text="Bước Tiến ▶", font=("Segoe UI", 9), bg="#E1DFDA", relief="flat", padx=8, command=self.step_next, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=3)
        add_hover_effect(self.btn_next, "#E1DFDA", "#D0CCC3")

        self.btn_auto = tk.Button(result_buttons_frame, text="🔄 Chạy Auto", font=("Segoe UI", 9, "bold"), bg="#2196F3", fg="white", activebackground="#1E88E5", relief="flat", padx=8, command=self.toggle_auto_play, state=tk.DISABLED)
        self.btn_auto.pack(side=tk.LEFT, padx=5)
        add_hover_effect(self.btn_auto, "#2196F3", "#1e88e5")

        self.btn_reset = tk.Button(result_buttons_frame, text="↻ Reset", font=("Segoe UI", 9), bg="#E1DFDA", relief="flat", padx=8, command=self.handle_reset, state=tk.DISABLED)
        self.btn_reset.pack(side=tk.LEFT, padx=3)
        add_hover_effect(self.btn_reset, "#E1DFDA", "#D0CCC3")

        # Thanh trượt tốc độ chạy tự động
        tk.Label(result_buttons_frame, text="Auto (ms):", font=("Segoe UI", 9), bg=COLOR_BG).pack(side=tk.LEFT, padx=(10, 3))
        self.scale_speed = tk.Scale(result_buttons_frame, from_=200, to=2000, orient=tk.HORIZONTAL, length=100, bg=COLOR_BG, highlightthickness=0, fg=COLOR_TEXT_MAIN)
        self.scale_speed.set(500) # Mặc định là 500ms
        self.scale_speed.pack(side=tk.LEFT)

        # 4. Bảng Puzzle hiện tại (nằm dưới cùng bên trái) (Giảm pady dọc xuống 6)
        self.frame_current = tk.LabelFrame(left_col, text=" Bảng chạy mô phỏng hiện tại (A & B) ",
                                      font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=12, pady=6)
        self.frame_current.pack(fill=tk.BOTH, expand=True, pady=(3, 0))

        # Khung chứa 2 bảng mô phỏng side-by-side
        sim_grids_container = tk.Frame(self.frame_current, bg=COLOR_BG)
        sim_grids_container.pack(fill=tk.BOTH, expand=True)

        # Mô phỏng A
        self.frame_current_A = tk.LabelFrame(sim_grids_container, text=" Mô phỏng A ",
                                        font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=5, pady=2)
        self.frame_current_A.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
        self.current_tiles_A = []
        self.board_current_A = self.create_puzzle_grid_ui(self.frame_current_A, self.current_tiles_A, self.trang_thai_dau_A)

        # Mô phỏng B
        self.frame_current_B = tk.LabelFrame(sim_grids_container, text=" Mô phỏng B ",
                                        font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=5, pady=2)
        self.frame_current_B.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.current_tiles_B = []
        self.board_current_B = self.create_puzzle_grid_ui(self.frame_current_B, self.current_tiles_B, self.trang_thai_dau_B)

        self.lbl_step_counter = tk.Label(self.frame_current, text="Trạng thái: Đang đợi giải...",
                                         font=("Segoe UI", 10, "bold"), fg=COLOR_SUCCESS, bg=COLOR_BG)
        self.lbl_step_counter.pack(pady=(5, 0))

        # =====================================================================
        # THIẾT KẾ CỘT PHẢI (STATISTICS & TRACE LOGS)
        # =====================================================================

        # 0. Hướng dẫn sử dụng (Collapsible)
        guide_frame = tk.LabelFrame(right_col, text=" Huong dan su dung ",
                                    font=("Segoe UI", 11, "bold"), fg="#1565C0", bg=COLOR_BG, padx=10, pady=5)
        guide_frame.pack(fill=tk.X, pady=(0, 5))

        self.guide_visible = True
        self.guide_content = tk.Frame(guide_frame, bg=COLOR_BG)
        self.guide_content.pack(fill=tk.X)

        guide_steps = [
            ("B1.", "Chọn thuật toán", "Chọn thuật toán muốn dùng từ danh sách Combobox. Giao diện sẽ tự động thay đổi phù hợp."),
            ("B2.", "Shuffle (Sinh đề)", "Nhấn nút này để sinh đề bài ngẫu nhiên mới (luôn đảm bảo giải được)."),
            ("B3.", "Chạy Giải", "Nhấn để bắt đầu chạy thuật toán tìm lời giải. Kết quả hiện ở Trace Log."),
            ("B4.", "Xem kết quả", "Sau khi giải xong, dùng các nút bên dưới để xem từng bước:"),
        ]

        for step_title, btn_name, desc in guide_steps:
            row = tk.Frame(self.guide_content, bg=COLOR_BG)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"{step_title} {btn_name}:", font=("Segoe UI", 9, "bold"),
                     fg="#333", bg=COLOR_BG, anchor="w").pack(anchor="w")
            tk.Label(row, text=f"   {desc}", font=("Segoe UI", 8),
                     fg="#555", bg=COLOR_BG, anchor="w", wraplength=380, justify="left").pack(anchor="w")

        # Sub-buttons explanation
        sub_frame = tk.Frame(self.guide_content, bg="#F0EFE8", padx=8, pady=4)
        sub_frame.pack(fill=tk.X, pady=(2, 3))
        sub_items = [
            ("Bước Lùi / Bước Tiến", "Xem từng bước lời giải (lùi/tiến)."),
            ("Chạy Auto", "Tự động phát các bước liên tục. Kéo thanh Auto (ms) để chỉnh tốc độ."),
            ("Dừng", "Dừng khẩn cấp khi thuật toán đang chạy quá lâu."),
            ("Reset", "Quay về trạng thái ban đầu, sẵn sàng chạy lại."),
        ]
        for btn_name, desc in sub_items:
            tk.Label(sub_frame, text=f"- {btn_name}: {desc}", font=("Segoe UI", 8),
                     fg="#444", bg="#F0EFE8", anchor="w", wraplength=370, justify="left").pack(anchor="w", pady=1)

        # Toggle button
        def toggle_guide():
            if self.guide_visible:
                self.guide_content.pack_forget()
                btn_toggle.config(text="▼ Hiện hướng dẫn")
            else:
                self.guide_content.pack(fill=tk.X)
                btn_toggle.config(text="▲ Ẩn hướng dẫn")
            self.guide_visible = not self.guide_visible

        btn_toggle = tk.Button(guide_frame, text="▲ Ẩn hướng dẫn", font=("Segoe UI", 8),
                               bg="#E1DFDA", fg="#555", relief="flat", padx=6, pady=1,
                               command=toggle_guide)
        btn_toggle.pack(anchor="e", pady=(2, 0))

        # 1. Bảng thống kê (Giảm pady xuống 5)
        stats_frame = tk.LabelFrame(right_col, text=" Thống kê kết quả ",
                                    font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=12, pady=5)
        stats_frame.pack(fill=tk.X, pady=(0, 5))

        self.lbl_stat_steps = tk.Label(stats_frame, text="• Số bước di chuyển: --", font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_stat_steps.pack(fill=tk.X, pady=2)

        self.lbl_stat_nodes = tk.Label(stats_frame, text="• Tổng số Node đã xét: --", font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_stat_nodes.pack(fill=tk.X, pady=2)

        self.lbl_stat_time = tk.Label(stats_frame, text="• Thời gian giải: --", font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_stat_time.pack(fill=tk.X, pady=2)

        # 2. Khung Trace log thuật toán
        trace_frame = tk.LabelFrame(right_col, text=" Trace Log - Nhật ký thuật toán ",
                                    font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG, padx=8, pady=5)
        trace_frame.pack(fill=tk.BOTH, expand=True)

        self.text_log = tk.Text(trace_frame, wrap=tk.WORD, font=("Consolas", 8), bg="#FAF9F7", fg="#333", borderwidth=1, relief="solid")
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(trace_frame, command=self.text_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_log.config(yscrollcommand=scrollbar.set)

        self.log_message("Sẵn sàng! Nhấn 'Shuffle' để sinh đề hoặc nhấn 'Chạy Giải' để tìm lời giải ngay.")

    def on_algo_changed(self, event=None):
        algo_name = self.cbo_algo.get()
        is_standard = algo_name in [
            "BFS", "DFS", "IDS", "UCS", "A*",
            "Leo đồi đơn giản", "Leo đồi dốc nhất", "Greedy", "Giả lập luyện kim", "Beam search k=2",
            "CSP Backtracking", "CSP Forward Checking", "CSP Min-Conflicts"
        ]
        
        if is_standard:
            self.frame_start_B.pack_forget()
            self.frame_current_B.pack_forget()
            self.frame_goal_1.pack_forget()
            self.frame_goal_2.pack_forget()
            self.frame_goal_partial.pack_forget()
            
            self.frame_goal_1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
            self.frame_goal.config(text=" Trạng thái Đích ")
            self.frame_start_A.config(text=" Trạng thái Đầu ")
            self.frame_current_A.config(text=" Mô phỏng hiện tại ")
            
            self.frame_start.config(text=" Trạng thái ban đầu ")
            self.frame_current.config(text=" Bảng chạy mô phỏng hiện tại ")
            self.update_puzzle_grids()
            return

        self.frame_start_B.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.frame_current_B.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.frame_start_A.pack_configure(padx=(0, 5))
        self.frame_current_A.pack_configure(padx=(0, 5))
        if "Môi trường nhìn thấy 1 phần" in algo_name:
            # Ẩn 2 board đích thông thường
            self.frame_goal_1.pack_forget()
            self.frame_goal_2.pack_forget()
            # Hiện board đích nhìn thấy 1 phần
            self.frame_goal_partial.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.frame_goal.config(text=" Trạng thái Đích (Nhìn thấy 1 phần) ")
            self.frame_start_A.config(text=" Trạng thái A (1 phần) ")
            self.frame_start_B.config(text=" Trạng thái B (1 phần) ")
            self.frame_current_A.config(text=" Mô phỏng A (1 phần) ")
            self.frame_current_B.config(text=" Mô phỏng B (1 phần) ")
        else:
            # Ẩn board đích nhìn thấy 1 phần
            self.frame_goal_partial.pack_forget()
            # Hiện 2 board đích thông thường
            self.frame_goal_1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
            self.frame_goal_2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.frame_goal.config(text=" Trạng thái Đích (1 trong 2) ")
            self.frame_start_A.config(text=" Trạng thái A ")
            self.frame_start_B.config(text=" Trạng thái B ")
            self.frame_current_A.config(text=" Mô phỏng A ")
            self.frame_current_B.config(text=" Mô phỏng B ")
            
        self.frame_start.config(text=" Trạng thái ban đầu (A & B) ")
        self.frame_current.config(text=" Bảng chạy mô phỏng hiện tại (A & B) ")
        self.update_puzzle_grids()

    def create_puzzle_grid_ui(self, parent, tile_list, default_state):
        """
        Hàm tạo giao diện bảng 3x3 chứa các ô số trượt sử dụng Absolute Positioning (.place).
        """
        TILE_SIZE = 55
        TILE_GAP = 4
        BOARD_SIZE = 3 * TILE_SIZE + 4 * TILE_GAP
        
        grid_container = tk.Frame(parent, width=BOARD_SIZE, height=BOARD_SIZE, bg="#D6D8DB")
        grid_container.pack(expand=True, padx=5, pady=5)
        grid_container.pack_propagate(False)

        for i in range(9):
            row = i // 3
            col = i % 3
            val = default_state[i]

            x = TILE_GAP + col * (TILE_SIZE + TILE_GAP)
            y = TILE_GAP + row * (TILE_SIZE + TILE_GAP)

            tile = tk.Label(grid_container, text=str(val) if val != 0 else "",
                            font=("Segoe UI", 16, "bold"),
                            bg=COLOR_CARD if val != 0 else COLOR_EMPTY,
                            fg=COLOR_TEXT_MAIN, relief="flat", bd=0)
            tile.place(x=x, y=y, width=TILE_SIZE, height=TILE_SIZE)
            tile_list.append(tile)
            
        return grid_container

    # =====================================================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN GIAO DIỆN (UI EVENTS)
    # =====================================================================
    def log_message(self, text):
        """
        Ghi log nhật ký vào khung Trace Log và tự động cuộn xuống dưới.
        """
        self.text_log.insert(tk.END, text + "\n")
        self.text_log.see(tk.END)

    def update_puzzle_grids(self):
        """
        Cập nhật lại hình ảnh các số trên 3 bảng tương ứng với biến trạng thái.
        """
        algo_name = self.cbo_algo.get()
        is_partial = "Môi trường nhìn thấy 1 phần" in algo_name

        # 1. Cập nhật Bảng ban đầu A và B
        for i, val in enumerate(self.trang_thai_dau_A):
            if is_partial:
                if i in self.known_indices:
                    self.start_tiles_A[i].config(text=str(val) if val != 0 else "",
                                                 bg=COLOR_CARD if val != 0 else COLOR_EMPTY)
                else:
                    self.start_tiles_A[i].config(text="?", bg=COLOR_EMPTY)
            else:
                self.start_tiles_A[i].config(text=str(val) if val != 0 else "",
                                             bg=COLOR_CARD if val != 0 else COLOR_EMPTY)

        for i, val in enumerate(self.trang_thai_dau_B):
            if is_partial:
                if i in self.known_indices:
                    self.start_tiles_B[i].config(text=str(val) if val != 0 else "",
                                                 bg=COLOR_CARD if val != 0 else COLOR_EMPTY)
                else:
                    self.start_tiles_B[i].config(text="?", bg=COLOR_EMPTY)
            else:
                self.start_tiles_B[i].config(text=str(val) if val != 0 else "",
                                             bg=COLOR_CARD if val != 0 else COLOR_EMPTY)

        # Cập nhật bảng đích nhìn thấy 1 phần nếu ở chế độ này
        if is_partial:
            goal_state = CANDIDATE_GOALS[self.active_goal_index]
            for i, val in enumerate(goal_state):
                if i in self.known_indices:
                    self.goal_tiles_partial[i].config(text=str(val) if val != 0 else "",
                                                      bg=COLOR_CARD if val != 0 else COLOR_EMPTY)
                else:
                    self.goal_tiles_partial[i].config(text="?", bg=COLOR_EMPTY)

        # 2. Cập nhật Bảng chạy mô phỏng hiện tại A và B
        state_A = self.trang_thai_dau_A
        state_B = self.trang_thai_dau_B

        if self.duong_di_loi_giai and 0 <= self.index_buoc_hien_tai < len(self.duong_di_loi_giai):
            item = self.duong_di_loi_giai[self.index_buoc_hien_tai]
            if isinstance(item, tuple):
                state_A, state_B = item
            else:
                state_A = item
                state_B = self.trang_thai_dau_B

        for i, val in enumerate(state_A):
            if is_partial:
                if i in self.known_indices:
                    if val is None:
                        self.current_tiles_A[i].config(text="", bg=COLOR_EMPTY)
                    else:
                        self.current_tiles_A[i].config(text=str(val) if val != 0 else "", bg=COLOR_CARD if val != 0 else COLOR_EMPTY)
                else:
                    self.current_tiles_A[i].config(text="?", bg=COLOR_EMPTY)
            else:
                if val is None:
                    self.current_tiles_A[i].config(text="", bg=COLOR_EMPTY)
                else:
                    self.current_tiles_A[i].config(text=str(val) if val != 0 else "", bg=COLOR_CARD if val != 0 else COLOR_EMPTY)

        for i, val in enumerate(state_B):
            if is_partial:
                if i in self.known_indices:
                    self.current_tiles_B[i].config(text=str(val) if val != 0 else "",
                                                   bg=COLOR_CARD if val != 0 else COLOR_EMPTY)
                else:
                    self.current_tiles_B[i].config(text="?", bg=COLOR_EMPTY)
            else:
                self.current_tiles_B[i].config(text=str(val) if val != 0 else "",
                                               bg=COLOR_CARD if val != 0 else COLOR_EMPTY)

        # Cập nhật nhãn đếm bước
        if not self.duong_di_loi_giai:
            self.lbl_step_counter.config(text="Trạng thái: Đang đợi giải...", fg=COLOR_ACCENT)
        else:
            total_steps = len(self.duong_di_loi_giai) - 1
            if self.index_buoc_hien_tai == 0:
                self.lbl_step_counter.config(text=f"Bước hiện tại: 0 / {total_steps} (Trạng thái đầu)", fg=COLOR_ACCENT)
            elif self.index_buoc_hien_tai == total_steps:
                # Kiểm tra xem có đạt đích hay không
                is_standard = algo_name in [
                    "BFS thường", "DFS thường", "IDS thường", "UCS thường", "A* thường",
                    "Leo đồi đơn giản", "Leo đồi dốc nhất", "Greedy", "Giả lập luyện kim", "Beam search k=2"
                ]
                if is_partial:
                    target_goal = CANDIDATE_GOALS[self.active_goal_index]
                    dat_dich_A = (list(state_A) == target_goal)
                    dat_dich_B = (list(state_B) == target_goal)
                elif is_standard:
                    dat_dich_A = (list(state_A) == GOAL_STATE)
                    dat_dich_B = True
                else:
                    dat_dich_A = (list(state_A) in GOAL_STATES)
                    dat_dich_B = (list(state_B) in GOAL_STATES)

                if dat_dich_A and dat_dich_B:
                    self.lbl_step_counter.config(text=f"Bước hiện tại: {self.index_buoc_hien_tai} / {total_steps} (Hoàn thành đích! 🎉)", fg=COLOR_SUCCESS)
                else:
                    self.lbl_step_counter.config(text=f"Bước hiện tại: {self.index_buoc_hien_tai} / {total_steps} (Dừng - )", fg="#F44336")
            else:
                self.lbl_step_counter.config(text=f"Bước hiện tại: {self.index_buoc_hien_tai} / {total_steps}", fg="#1E88E5")

    def handle_shuffle(self):
        """
        Xử lý khi người dùng nhấn nút Shuffle. Sinh ra các trạng thái đầu mới.
        """
        # Nếu đang chạy tự động thì dừng lại
        self.dang_chay_auto = False

        algo_name = self.cbo_algo.get()
        is_partial = "Môi trường nhìn thấy 1 phần" in algo_name

        is_standard = algo_name in [
            "BFS", "DFS", "IDS", "UCS", "A*",
            "Leo đồi đơn giản", "Leo đồi dốc nhất", "Greedy", "Giả lập luyện kim", "Beam search k=2",
            "CSP Backtracking", "CSP Forward Checking", "CSP Min-Conflicts"
        ]
        
        if is_standard:
            self.trang_thai_dau_A = sinh_de_ngau_nhien([GOAL_STATE], so_buoc=15)
        elif is_partial:
            self.active_goal_index = random.choice([0, 1, 2])
            num_visible = random.choice([2, 3])
            self.known_indices = sorted(random.sample(range(9), num_visible))
            
            target_goal = CANDIDATE_GOALS[self.active_goal_index]
            self.trang_thai_dau_A = sinh_de_ngau_nhien([target_goal], so_buoc=3)
            self.trang_thai_dau_B = sinh_de_ngau_nhien([target_goal], so_buoc=3)
        else:
            self.trang_thai_dau_A = sinh_de_ngau_nhien(GOAL_STATES, so_buoc=3)
            self.trang_thai_dau_B = sinh_de_ngau_nhien(GOAL_STATES, so_buoc=3)

        self.duong_di_loi_giai = []
        self.index_buoc_hien_tai = 0

        # Cập nhật UI
        self.update_puzzle_grids()

        # Reset thông số thống kê
        self.lbl_stat_steps.config(text="• Số bước di chuyển: --")
        self.lbl_stat_nodes.config(text="• Tổng số Node đã xét: --")
        self.lbl_stat_time.config(text="• Thời gian giải: --")

        # Reset trạng thái các nút điều khiển kết quả
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED, text="🔄 Chạy Auto")
        self.btn_reset.config(state=tk.DISABLED)

        self.text_log.delete('1.0', tk.END)
        if is_partial:
            self.log_message(f"[1 phần] Chọn đích CANDIDATE_GOALS[{self.active_goal_index}] làm Đích thực tế.")
            self.log_message(f"[1 phần] Chỉ nhìn thấy {num_visible} vị trí ô: {self.known_indices}")
        self.log_message(f"Bảng A vừa sinh ngẫu nhiên: {self.trang_thai_dau_A}")
        self.log_message(f"Bảng B vừa sinh ngẫu nhiên: {self.trang_thai_dau_B}")
        self.log_message("Nhấn nút 'Chạy Giải' để bắt đầu tìm kiếm lời giải.")

    def handle_reset(self):
        """
        Reset bảng chạy mô phỏng hiện tại về trạng thái ban đầu của lời giải.
        """
        self.index_buoc_hien_tai = 0
        self.dang_chay_auto = False
        self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")
        self.update_puzzle_grids()
        self.btn_prev.config(state=tk.DISABLED)
        if len(self.duong_di_loi_giai) > 1:
            self.btn_next.config(state=tk.NORMAL)

    def animate_transition(self, old_item, new_item, direction, on_complete=None):
        old_A, old_B = (old_item if isinstance(old_item, tuple) else (old_item, self.trang_thai_dau_B))
        new_A, new_B = (new_item if isinstance(new_item, tuple) else (new_item, self.trang_thai_dau_B))

        def get_diff(old_s, new_s):
            diffs = [i for i in range(9) if old_s[i] != new_s[i]]
            if len(diffs) == 2:
                if old_s[diffs[0]] == 0 and new_s[diffs[1]] == 0 and old_s[diffs[1]] == new_s[diffs[0]]:
                    return old_s[diffs[1]], diffs[1], diffs[0]
                elif old_s[diffs[1]] == 0 and new_s[diffs[0]] == 0 and old_s[diffs[0]] == new_s[diffs[1]]:
                    return old_s[diffs[0]], diffs[0], diffs[1]
            return None

        diff_A = get_diff(old_A, new_A)
        diff_B = get_diff(old_B, new_B)

        if not diff_A and not diff_B:
            if on_complete: on_complete()
            return

        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)

        frames = 8
        duration = 120 # ms
        delay = duration // frames
        TILE_SIZE = 55
        TILE_GAP = 4

        float_A, float_B = None, None
        x_src_A, y_src_A, x_dst_A, y_dst_A = 0, 0, 0, 0
        x_src_B, y_src_B, x_dst_B, y_dst_B = 0, 0, 0, 0

        if diff_A:
            val, src, dst = diff_A
            if direction == -1: src, dst = dst, src
            self.current_tiles_A[src].config(text="", bg=COLOR_EMPTY)
            r_src, c_src = src // 3, src % 3
            r_dst, c_dst = dst // 3, dst % 3
            x_src_A, y_src_A = TILE_GAP + c_src * (TILE_SIZE + TILE_GAP), TILE_GAP + r_src * (TILE_SIZE + TILE_GAP)
            x_dst_A, y_dst_A = TILE_GAP + c_dst * (TILE_SIZE + TILE_GAP), TILE_GAP + r_dst * (TILE_SIZE + TILE_GAP)
            float_A = tk.Label(self.board_current_A, text=str(val), font=("Segoe UI", 16, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN, relief="flat", bd=0)
            float_A.place(x=x_src_A, y=y_src_A, width=TILE_SIZE, height=TILE_SIZE)

        if diff_B:
            val, src, dst = diff_B
            if direction == -1: src, dst = dst, src
            self.current_tiles_B[src].config(text="", bg=COLOR_EMPTY)
            r_src, c_src = src // 3, src % 3
            r_dst, c_dst = dst // 3, dst % 3
            x_src_B, y_src_B = TILE_GAP + c_src * (TILE_SIZE + TILE_GAP), TILE_GAP + r_src * (TILE_SIZE + TILE_GAP)
            x_dst_B, y_dst_B = TILE_GAP + c_dst * (TILE_SIZE + TILE_GAP), TILE_GAP + r_dst * (TILE_SIZE + TILE_GAP)
            float_B = tk.Label(self.board_current_B, text=str(val), font=("Segoe UI", 16, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN, relief="flat", bd=0)
            float_B.place(x=x_src_B, y=y_src_B, width=TILE_SIZE, height=TILE_SIZE)

        def anim_step(frame):
            if frame <= frames:
                progress = frame / frames
                if float_A: float_A.place(x=x_src_A + (x_dst_A - x_src_A) * progress, y=y_src_A + (y_dst_A - y_src_A) * progress)
                if float_B: float_B.place(x=x_src_B + (x_dst_B - x_src_B) * progress, y=y_src_B + (y_dst_B - y_src_B) * progress)
                self.root.after(delay, lambda: anim_step(frame + 1))
            else:
                if float_A: float_A.destroy()
                if float_B: float_B.destroy()
                if on_complete: on_complete()

        anim_step(1)

    def step_next(self, is_auto=False):
        if self.is_animating: return
        if self.duong_di_loi_giai and self.index_buoc_hien_tai < len(self.duong_di_loi_giai) - 1:
            old_item = self.duong_di_loi_giai[self.index_buoc_hien_tai]
            self.index_buoc_hien_tai += 1
            new_item = self.duong_di_loi_giai[self.index_buoc_hien_tai]

            self.is_animating = True
            def on_anim_done():
                self.is_animating = False
                self.update_puzzle_grids()
                self.btn_prev.config(state=tk.NORMAL)
                if self.index_buoc_hien_tai < len(self.duong_di_loi_giai) - 1:
                    self.btn_next.config(state=tk.NORMAL)
                else:
                    self.btn_next.config(state=tk.DISABLED)
                    if self.dang_chay_auto:
                        self.dang_chay_auto = False
                        self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")
                if is_auto and self.dang_chay_auto:
                    speed_ms = self.scale_speed.get()
                    self.root.after(speed_ms, self.run_auto_play_loop)
            self.animate_transition(old_item, new_item, direction=1, on_complete=on_anim_done)

    def step_prev(self):
        if self.is_animating: return
        if self.duong_di_loi_giai and self.index_buoc_hien_tai > 0:
            old_item = self.duong_di_loi_giai[self.index_buoc_hien_tai]
            self.index_buoc_hien_tai -= 1
            new_item = self.duong_di_loi_giai[self.index_buoc_hien_tai]

            self.is_animating = True
            def on_anim_done():
                self.is_animating = False
                self.update_puzzle_grids()
                self.btn_next.config(state=tk.NORMAL)
                if self.index_buoc_hien_tai > 0:
                    self.btn_prev.config(state=tk.NORMAL)
                else:
                    self.btn_prev.config(state=tk.DISABLED)
            self.animate_transition(old_item, new_item, direction=-1, on_complete=on_anim_done)

    def toggle_auto_play(self):
        if not self.duong_di_loi_giai: return
        if self.dang_chay_auto:
            self.dang_chay_auto = False
            self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")
            self.log_message("[Auto] Đã tạm dừng chạy tự động.")
        else:
            self.dang_chay_auto = True
            self.btn_auto.config(text="⏸ Dừng Auto", bg="#FF9800")
            self.log_message("[Auto] Bắt đầu chạy tự động mô phỏng các bước...")
            if self.index_buoc_hien_tai >= len(self.duong_di_loi_giai) - 1:
                self.index_buoc_hien_tai = 0
                self.update_puzzle_grids()
            self.run_auto_play_loop()

    def run_auto_play_loop(self):
        if not self.dang_chay_auto: return
        if self.index_buoc_hien_tai < len(self.duong_di_loi_giai) - 1:
            self.step_next(is_auto=True)
        else:
            self.dang_chay_auto = False
            self.btn_auto.config(text="🔄 Chạy Auto", bg="#2196F3")
            self.log_message("[Auto] Hoàn thành trình diễn lời giải!")

    # =====================================================================
    # XỬ LÝ KHÁM PHÁ THUẬT TOÁN ĐA LUỒNG (THREADING)
    # =====================================================================
    def start_solving_thread(self):
        """
        Khởi động luồng phụ chạy thuật toán tìm kiếm lời giải.
        """
        algo_name = self.cbo_algo.get()
        is_partial = "Môi trường nhìn thấy 1 phần" in algo_name

        is_standard = algo_name in [
            "BFS", "DFS", "IDS", "UCS", "A*",
            "Leo đồi đơn giản", "Leo đồi dốc nhất", "Greedy", "Giả lập luyện kim", "Beam search k=2",
            "CSP Backtracking", "CSP Forward Checking", "CSP Min-Conflicts"
        ]
        if is_standard:
            already_solved = (list(self.trang_thai_dau_A) == GOAL_STATE)
        elif is_partial:
            target_goal = CANDIDATE_GOALS[self.active_goal_index]
            already_solved = (list(self.trang_thai_dau_A) == target_goal and list(self.trang_thai_dau_B) == target_goal)
        else:
            already_solved = (self.trang_thai_dau_A in GOAL_STATES and self.trang_thai_dau_B in GOAL_STATES)

        if already_solved:
            messagebox.showinfo("Thông báo", "Cả 2 bảng hiện tại đã ở trạng thái Đích rồi!")
            return

        self.dang_chay_giai = True
        self.flag_dung_giai = False
        self.text_log.delete('1.0', tk.END)

        # Thay đổi trạng thái các nút
        self.btn_solve.config(state=tk.DISABLED, text="⌛ Đang tìm...")
        self.btn_shuffle.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.DISABLED)

        # Khởi chạy luồng phụ
        threading.Thread(target=self.solve_puzzle, daemon=True).start()

    def stop_solving(self):
        """
        Nút dừng khẩn cấp khi thuật toán đang tìm kiếm.
        """
        if self.dang_chay_giai:
            self.flag_dung_giai = True
            self.log_message("\n⚠️ ĐANG YÊU CẦU DỪNG TÌM KIẾM KHẨN CẤP...")

    def check_stop_flag(self):
        """
        Trả về True nếu người dùng yêu cầu dừng khẩn cấp.
        """
        return self.flag_dung_giai

    def solve_puzzle(self):
        """
        Thực hiện tìm kiếm lời giải bằng thuật toán được chọn từ Combobox.
        """
        algo_name = self.cbo_algo.get()
        is_partial = "Môi trường nhìn thấy 1 phần" in algo_name
        start_time = time.time()

        self.log_message(f"=== BẮT ĐẦU GIẢI PUZZLE BẰNG THUẬT TOÁN: {algo_name} ===")
        self.log_message(f"Trạng thái A: {self.trang_thai_dau_A}")
        self.log_message(f"Trạng thái B: {self.trang_thai_dau_B}")
        is_standard = algo_name in [
            "BFS", "DFS", "IDS", "UCS", "A*",
            "Leo đồi đơn giản", "Leo đồi dốc nhất", "Greedy", "Giả lập luyện kim", "Beam search k=2",
            "CSP Backtracking", "CSP Forward Checking", "CSP Min-Conflicts"
        ]
        if is_standard:
            self.log_message(f"Trạng thái Đích: {GOAL_STATE}")
        elif is_partial:
            self.log_message(f"Trạng thái Đích (Ẩn/1 phần): {CANDIDATE_GOALS[self.active_goal_index]}")
        else:
            self.log_message(f"Trạng thái Đích 1: {GOAL_STATES[0]}")
            self.log_message(f"Trạng thái Đích 2: {GOAL_STATES[1]}")

        loi_giai = None
        dem_node = 0

        try:
            if algo_name == "BFS":
                loi_giai, dem_node = BFS_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "DFS":
                loi_giai, dem_node = DFS_Solver(self.trang_thai_dau_A, GOAL_STATE, limit=30, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "IDS":
                loi_giai, dem_node = IDS_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "UCS":
                loi_giai, dem_node = UCS_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "A*":
                loi_giai, dem_node = AStar_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "Leo đồi đơn giản":
                loi_giai, dem_node = Simple_Hill_Climbing_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "Leo đồi dốc nhất":
                loi_giai, dem_node = Steepest_Ascent_Hill_Climbing_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "Greedy":
                loi_giai, dem_node = Greedy_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "Giả lập luyện kim":
                loi_giai, dem_node = Simulated_Annealing_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "Beam search k=2":
                loi_giai, dem_node = Beam_Search_Solver(self.trang_thai_dau_A, GOAL_STATE, k=2, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "CSP Backtracking":
                self.log_message(">> GIẢI THÍCH THUẬT TOÁN CSP BACKTRACKING:")
                self.log_message("Mô hình hóa 8-Puzzle thành CSP: Lần lượt gán viên gạch (từ 1-8) vào 9 vị trí trên bàn cờ. Nếu vị trí không đúng với đích, thuật toán sẽ quay lui (Backtrack) để thử vị trí khác, thay vì thử các bước trượt.")
                loi_giai, dem_node = CSP_Backtracking_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "CSP Forward Checking":
                self.log_message(">> GIẢI THÍCH THUẬT TOÁN CSP FORWARD CHECKING:")
                self.log_message("Giống Backtracking, nhưng mỗi khi gán xong 1 ô, nó sẽ kiểm tra trước (Forward Check) và loại bỏ các lựa chọn sai lầm cho các ô còn lại, giúp giảm không gian tìm kiếm.")
                loi_giai, dem_node = CSP_Forward_Checking_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "CSP Min-Conflicts":
                self.log_message(">> GIẢI THÍCH THUẬT TOÁN CSP MIN-CONFLICTS:")
                self.log_message("Khởi tạo ngẫu nhiên vị trí các gạch (có thể bị xếp chồng). Tại mỗi bước, chọn 1 viên gạch đang sai vị trí và hoán đổi nó với vị trí đúng của nó để giảm thiểu tối đa số lượng xung đột.")
                loi_giai, dem_node = CSP_Min_Conflicts_Solver(self.trang_thai_dau_A, GOAL_STATE, log_callback=self.log_message, stop_flag=self.check_stop_flag)
            elif algo_name == "BFS (Initial Belief State)":
                loi_giai, dem_node = BFS_Belief_Solver(
                    self.trang_thai_dau_A,
                    self.trang_thai_dau_B,
                    log_callback=self.log_message,
                    stop_flag=self.check_stop_flag
                )
            elif algo_name == "DFS (Initial Belief State)":
                loi_giai, dem_node = DFS_Belief_Solver(
                    self.trang_thai_dau_A,
                    self.trang_thai_dau_B,
                    gioi_han_do_sau=25,
                    log_callback=self.log_message,
                    stop_flag=self.check_stop_flag
                )
            elif algo_name == "IDS (Initial Belief State)":
                loi_giai, dem_node = IDS_Belief_Solver(
                    self.trang_thai_dau_A,
                    self.trang_thai_dau_B,
                    log_callback=self.log_message,
                    stop_flag=self.check_stop_flag
                )
            elif is_partial:
                active_goal = CANDIDATE_GOALS[self.active_goal_index]
                target_goal = guess_goal(self.known_indices, active_goal)
                self.log_message(f"[Đoán Đích] Các ô đã biết tại {self.known_indices}: {[active_goal[i] for i in self.known_indices]}")
                self.log_message(f"[Đoán Đích] Đích đoán được: {target_goal}")

                if algo_name == "UCS (Môi trường nhìn thấy 1 phần)":
                    loi_giai, dem_node = UCS_Belief_Solver(
                        self.trang_thai_dau_A,
                        self.trang_thai_dau_B,
                        target_goal,
                        log_callback=self.log_message,
                        stop_flag=self.check_stop_flag
                    )
                elif algo_name == "Greedy (Môi trường nhìn thấy 1 phần)":
                    loi_giai, dem_node = Greedy_Belief_Solver(
                        self.trang_thai_dau_A,
                        self.trang_thai_dau_B,
                        target_goal,
                        log_callback=self.log_message,
                        stop_flag=self.check_stop_flag
                    )
                elif algo_name == "A* (Môi trường nhìn thấy 1 phần)":
                    loi_giai, dem_node = AStar_Belief_Solver(
                        self.trang_thai_dau_A,
                        self.trang_thai_dau_B,
                        target_goal,
                        log_callback=self.log_message,
                        stop_flag=self.check_stop_flag
                    )
        except Exception as e:
            self.log_message(f"\n❌ Đã xảy ra lỗi trong quá trình tính toán: {str(e)}")

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Đưa lệnh cập nhật GUI trở lại luồng chính (Main Thread)
        self.root.after(0, self.on_solving_finished, loi_giai, dem_node, elapsed_time)

    def on_solving_finished(self, loi_giai, dem_node, elapsed_time):
        """
        Cập nhật lại giao diện ngay sau khi quá trình tìm kiếm lời giải kết thúc.
        """
        self.dang_chay_giai = False
        self.btn_solve.config(state=tk.NORMAL, text="▶ Chạy Giải")
        self.btn_shuffle.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

        if self.flag_dung_giai:
            self.log_message("\n🛑 ĐÃ HỦY TÌM KIẾM THÀNH CÔNG THEO YÊU CẦU NGƯỜI DÙNG!")
            messagebox.showwarning("Hủy bỏ", "Quá trình tìm kiếm đã bị dừng ngang.")
            return

        if loi_giai:
            self.duong_di_loi_giai = loi_giai
            self.index_buoc_hien_tai = 0

            # Cập nhật bảng thống kê
            self.lbl_stat_steps.config(text=f"• Số bước di chuyển: {len(loi_giai) - 1} bước")
            self.lbl_stat_nodes.config(text=f"• Tổng số Node đã xét: {dem_node} nodes")
            self.lbl_stat_time.config(text=f"• Thời gian giải: {elapsed_time:.4f} giây")

            # Kích hoạt các nút trình diễn đường đi
            self.btn_prev.config(state=tk.DISABLED) # Đang ở bước 0 nên lùi bị disable
            self.btn_next.config(state=tk.NORMAL)
            self.btn_auto.config(state=tk.NORMAL)
            self.btn_reset.config(state=tk.NORMAL)

            self.log_message(f"\n✅ THÀNH CÔNG!")
            self.log_message(f"- Số bước trượt: {len(loi_giai) - 1}")
            self.log_message(f"- Tổng số node đã duyệt qua: {dem_node}")
            self.log_message(f"- Thời gian giải thuật: {elapsed_time:.4f} giây")
            self.log_message("- Hãy nhấn 'Chạy Auto' hoặc nút 'Tiến' để mô phỏng đường đi về đích.")

            messagebox.showinfo("Thành công", f"Tìm thấy lời giải có độ dài {len(loi_giai) - 1} bước di chuyển!")
        else:
            self.log_message("\n❌ THẤT BẠI: Không tìm thấy bất kỳ lời giải nào!")
            messagebox.showerror("Thất bại", "Không thể tìm thấy đường đi đến đích trong giới hạn cho phép.")

        self.update_puzzle_grids()


# =============================================================================
# KHỞI CHẠY CHƯƠNG TRÌNH CHÍNH
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
