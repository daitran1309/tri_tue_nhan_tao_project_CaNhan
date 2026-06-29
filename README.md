# Project cá nhân: Giải Trò Chơi 8-Puzzle Trực Quan (AI)

Đồ án môn học **Trí Tuệ Nhân Tạo**. Ứng dụng cung cấp một giao diện trực quan (GUI) được viết bằng `Tkinter` để mô phỏng và minh họa chi tiết quá trình hoạt động của các thuật toán tìm kiếm và tối ưu hóa khi giải quyết bài toán 8-Puzzle nổi tiếng.

## Thông tin Cá nhân
- **Học viên thực hiện:** Trần Phước Đại
- **Mã số sinh viên (MSSV):** 24110190
- **Lớp:** 252ARIN330585_07
- **Môn học:** Trí Tuệ Nhân Tạo (Artificial Intelligence)
- **Giảng viên hướng dẫn:** Phan Thị Huyền Trang

---

## 🎯 Tính năng nổi bật
- **Giao diện hiện đại & Mượt mà:** Bố cục rõ ràng, màu sắc hài hòa với hiệu ứng trượt ô (Sliding Animation) mô phỏng chân thực từng bước di chuyển.
- **Auto Play:** Chế độ tự động phát lại lời giải với khả năng tùy chỉnh tốc độ.
- **Hỗ trợ đa dạng Thuật toán:**
  - *Tìm kiếm mù (Uninformed Search):* BFS, DFS, IDS, UCS.
  - *Tìm kiếm có thông tin (Informed Search):* A*, Greedy.
  - *Tìm kiếm cục bộ (Local Search):* Leo đồi đơn giản (Simple Hill Climbing), Leo đồi dốc nhất (Steepest Ascent), Giả lập luyện kim (Simulated Annealing), Beam Search.
  - *Ràng buộc thỏa mãn (CSP - Constraint Satisfaction Problem):* Backtracking, Forward Checking, Min-Conflicts.
  - *Môi trường nhìn thấy 1 phần (Partial Observability / Belief States):* Thuật toán giải quyết khi chỉ biết một vài ô trên bàn cờ.
- **So sánh Trực quan:** Hỗ trợ mô phỏng chạy song song 2 bảng trạng thái (A và B).
- **Thống kê:** Đo lường chính xác số bước đi, số node đã duyệt (Nodes Expanded) và thời gian thực thi của từng thuật toán.

---

## 📂 Cấu trúc Thư mục

```text
baitap-code-AI/
│
├── main.py                     # File chính khởi chạy ứng dụng GUI
├── README.md                   # Tài liệu hướng dẫn sử dụng (file bạn đang đọc)
│
└── algorithms/                 # Package chứa toàn bộ logic của các thuật toán
    ├── __init__.py             # Import các thuật toán để main.py gọi
    ├── utils.py                # Chứa hằng số (Đích), hàm sinh đề ngẫu nhiên, hàm Heuristic...
    ├── bfs.py                  # Thuật toán Breadth-First Search
    ├── dfs.py                  # Thuật toán Depth-First Search
    ├── ids.py                  # Thuật toán Iterative Deepening Search (DLS & IDS)
    ├── ucs.py                  # Thuật toán Uniform-Cost Search
    ├── astar.py                # Thuật toán A* (A-Star)
    ├── greedy.py               # Thuật toán Greedy Best-First Search
    ├── hill_climbing.py        # Các thuật toán Leo đồi (Simple & Steepest)
    ├── simulated_annealing.py  # Thuật toán Giả lập luyện kim
    ├── beam_search.py          # Thuật toán Beam Search
    ├── csp.py                  # Các thuật toán CSP (Backtracking, Forward Checking, Min-Conflicts)
    └── belief_algorithms.py    # Các thuật toán xử lý Belief State (Môi trường nhìn thấy 1 phần)
```

---

## 🚀 Hướng dẫn Cài đặt & Chạy Ứng dụng

### Yêu cầu hệ thống:
- Hệ điều hành: Windows, macOS, hoặc Linux
- Python 3.7 trở lên

### Cách chạy:
1. Mở Terminal / Command Prompt tại thư mục dự án.
2. Chạy lệnh sau để khởi động phần mềm:
   ```bash
   python main.py
   ```
3. Giao diện chương trình sẽ tự động mở toàn màn hình (zoomed).

---

## 📖 Hướng dẫn Sử dụng Giao diện
1. **Chọn thuật toán:** Bấm vào danh sách thả xuống (Combobox) ở giữa màn hình. Khi chọn, một lời giải thích ngắn về thuật toán sẽ hiện ra ở khung Trace Log.
2. **Sinh đề:** Nhấn nút **"🔄 Shuffle"** để xáo trộn bảng khởi tạo ngẫu nhiên (luôn đảm bảo có lời giải).
3. **Chạy Giải:** Nhấn **"▶ Chạy Giải"** để bắt đầu thuật toán tìm kiếm đường đi.
4. **Xem mô phỏng:** 
   - Dùng nút **◀ Bước Lùi** và **Bước Tiến ▶** để trượt từng ô bằng tay.
   - Hoặc nhấn **🔄 Chạy Auto** để máy tự động phát lại các bước trượt (có thể chỉnh tốc độ ở thanh trượt bên cạnh).
   - Nút **↻ Reset** để đưa bàn cờ trở về trạng thái xuất phát ban đầu của đề bài.

---

*Cảm ơn Thầy/Cô đã xem xét đồ án môn học này!*
