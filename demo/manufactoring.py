import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import cv2
from pyzbar import pyzbar
import threading
import sys
import json
sys.path.append("../lib")
from lib.realtendant import add_users_to_workorder, get_all_mrp_productions, get_mrp_production_detail, get_all_workcenters, get_workorders_by_workcenter, export_all_employees_with_qr, get_workorder_detail

def scan_qr():
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh QR",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    if not file_path:
        messagebox.showinfo("Thông báo", "Bạn chưa chọn ảnh!")
        return
    image = cv2.imread(file_path)
    if image is None:
        messagebox.showerror("Lỗi", f"Không thể đọc ảnh: {file_path}")
        return
    decoded_objs = pyzbar.decode(image)
    qr_text_box.delete(1.0, tk.END)
    if not decoded_objs:
        qr_text_box.insert(tk.END, "Không tìm thấy mã QR trong ảnh!")
        return
    for obj in decoded_objs:
        qr_data = obj.data.decode("utf-8")
        qr_text_box.insert(tk.END, qr_data + "\n")
        try:
            data = json.loads(qr_data)
            print(data)
            if isinstance(data, dict) and 'user_id' in data:
                user_id_val = data['user_id']
                if isinstance(user_id_val, list):
                    user_id_val = user_id_val[0]
                if user_id_val:
                    add_employee_from_qr(data)
        except Exception:
            pass

def start_scan():
    threading.Thread(target=scan_qr, daemon=True).start()

def load_mrp_list():
    mrps = get_all_mrp_productions(fields=["id", "name"])
    mrp_listbox.delete(0, tk.END)
    for mrp in mrps:
        mrp_listbox.insert(tk.END, f"{mrp['id']}: {mrp['name']}")
    mrp_listbox.mrps = mrps  # lưu lại để tra cứu id nhanh

def load_workcenter_list():
    # Lấy tối giản trường, tránh trường liên kết lớn và giới hạn số lượng bản ghi
    try:
        workcenters = get_all_workcenters(fields=["id", "name", "code", "active", "company_id", "display_name"])
        # Nếu trả về quá nhiều, chỉ lấy 100 bản ghi đầu tiên để tránh treo máy
        if len(workcenters) > 100:
            workcenters = workcenters[:100]
    except Exception as e:
        workcenters = []
    wc_listbox.delete(0, tk.END)
    for wc in workcenters:
        wc_listbox.insert(tk.END, f"{wc['id']}: {wc['name']} ({wc.get('code', '')})")
    wc_listbox.workcenters = workcenters
    # Nếu không có workcenter thì clear luôn vùng detail và workorder
    if not workcenters:
        wc_detail_box.config(state=tk.NORMAL)
        wc_detail_box.delete(1.0, tk.END)
        wc_detail_box.config(state=tk.DISABLED)
        wc_workorder_listbox.delete(0, tk.END)
        wc_workorder_listbox.workorders = []

def on_mrp_select(event):
    selection = mrp_listbox.curselection()
    if not selection:
        return
    idx = selection[0]
    mrp = getattr(mrp_listbox, 'mrps', [])[idx]
    mrp_id = mrp['id']
    detail = get_mrp_production_detail(mrp_id)
    # Hiển thị chi tiết lệnh sản xuất
    detail_text = f"ID: {detail.get('id')}\nTên: {detail.get('name')}\nTrạng thái: {detail.get('state')}\nSản phẩm: {detail.get('product_id')}\nSố lượng: {detail.get('product_qty')}\nNgày bắt đầu: {detail.get('date_start')}\nNgày kết thúc: {detail.get('date_finished')}\n"
    detail_text_box.config(state=tk.NORMAL)
    detail_text_box.delete(1.0, tk.END)
    detail_text_box.insert(tk.END, detail_text)
    detail_text_box.config(state=tk.DISABLED)
    # Hiển thị danh sách hoạt động và user
    workorders = detail.get('workorders', [])
    workorder_text = ""
    for wo in workorders:
        workorder_text += f"- {wo.get('name')} (Trạng thái: {wo.get('state')})\n"
        users = wo.get('working_user_details', [])
        if users:
            for user in users:
                workorder_text += f"    + User: {user.get('name')} ({user.get('login')})\n"
        else:
            workorder_text += "    + Không có user\n"
    workorder_text_box.config(state=tk.NORMAL)
    workorder_text_box.delete(1.0, tk.END)
    workorder_text_box.insert(tk.END, workorder_text)
    workorder_text_box.config(state=tk.DISABLED)

def on_wo_select(event):
    global selected_workorder
    selection = wc_workorder_listbox.curselection()
    workorders = getattr(wc_workorder_listbox, 'workorders', [])
    if not workorders or not selection:
        selected_workorder_var.set("")
        selected_workorder = None
        return
    idx = selection[0]
    wo = workorders[idx]
    # Lưu lại id công đoạn đã chọn
    selected_workorder = wo
    # Chỉ cập nhật label công đoạn đã chọn, không reload hay xóa list công đoạn
    detail = f"Công đoạn đã chọn: {wo.get('id')}: {wo.get('name')} (Trạng thái: {wo.get('state')})"
    detail_workorder = get_workorder_detail(workorder_id=wo.get('id'))
    selected_workorder_var.set(detail)
    # Store duration_expected for countdown
    global expected_duration_seconds
    try:
        expected_duration_seconds = int(float(detail_workorder.get('duration_expected', 0))* 60)
    except Exception:
        expected_duration_seconds = 0
    # Fill 'Chi tiết lệnh sản xuất' box with detail_workorder fields
    detail_text = (
        f"Tên: {detail_workorder.get('name', '')}\n"
        f"Máy thực hiện: {detail_workorder.get('workcenter_id', '')[-1]}\n"
        f"Sản phẩm: {detail_workorder.get('product_id', '')[-1]}\n"
        f"Số lượng ước tính: {detail_workorder.get('qty_produced', '')}\n"
        f"Thời lượng dự kiến: {detail_workorder.get('duration_expected', '')}\n"
        f"Trạng thái: {detail_workorder.get('state', '')}\n"
    )
    detail_text_box.config(state=tk.NORMAL)
    detail_text_box.delete(1.0, tk.END)
    detail_text_box.insert(tk.END, detail_text)
    detail_text_box.config(state=tk.DISABLED)
    # Không động chạm gì đến CURRENT_MACHINE_INDEX, không reload lại list công đoạn

# Hàm này dùng để lấy lại danh sách công đoạn cho máy đang chọn (nếu cần refresh thủ công)
def refresh_workorders_for_current_machine():
    if CURRENT_MACHINE_INDEX is None:
        wc_workorder_listbox.delete(0, tk.END)
        wc_workorder_listbox.workorders = []
        return
    workcenters = getattr(wc_listbox, 'workcenters', None)
    if not workcenters or CURRENT_MACHINE_INDEX >= len(workcenters):
        wc_workorder_listbox.delete(0, tk.END)
        wc_workorder_listbox.workorders = []
        return
    wc = workcenters[CURRENT_MACHINE_INDEX]
    workorders = get_workorders_by_workcenter(wc.get('id'))
    wc_workorder_listbox.delete(0, tk.END)
    for wo in workorders:
        wc_workorder_listbox.insert(tk.END, f"{wo.get('id')}: {wo.get('name')} (Trạng thái: {wo.get('state')})")
    wc_workorder_listbox.workorders = workorders
def on_wc_select(event):
    global CURRENT_MACHINE_INDEX
    selection = wc_listbox.curselection()
    # Nếu không có workcenter nào hoặc không chọn thì để trắng cả 2 box
    if not getattr(wc_listbox, 'workcenters', None) or not wc_listbox.workcenters:
        wc_detail_box.config(state=tk.NORMAL)
        wc_detail_box.delete(1.0, tk.END)
        wc_detail_box.config(state=tk.DISABLED)
        wc_workorder_listbox.delete(0, tk.END)
        wc_workorder_listbox.workorders = []
        return
    if not selection:
        wc_detail_box.config(state=tk.NORMAL)
        wc_detail_box.delete(1.0, tk.END)
        wc_detail_box.config(state=tk.DISABLED)
        wc_workorder_listbox.delete(0, tk.END)
        wc_workorder_listbox.workorders = []
        return
    idx = selection[0]
    CURRENT_MACHINE_INDEX = idx
    wc = wc_listbox.workcenters[idx]
    wc_detail = f"ID: {wc.get('id')}\nTên: {wc.get('name')}\nMã: {wc.get('code')}\nCông ty: {wc.get('company_id')}\nHoạt động: {'Có' if wc.get('active') else 'Không'}\n"
    wc_detail_box.config(state=tk.NORMAL)
    wc_detail_box.delete(1.0, tk.END)
    wc_detail_box.insert(tk.END, wc_detail)
    wc_detail_box.config(state=tk.DISABLED)
    # Hiển thị danh sách workorder trên workcenter
    workorders = get_workorders_by_workcenter(wc.get('id'))
    wc_workorder_listbox.delete(0, tk.END)
    for wo in workorders:
        wc_workorder_listbox.insert(tk.END, f"{wo.get('id')}: {wo.get('name')} (Trạng thái: {wo.get('state')})")
    wc_workorder_listbox.workorders = workorders
    # Render lại bản đồ máy với máy đang chọn
    workcenters = getattr(wc_listbox, 'workcenters', None)
    render_machine_map(workcenters, CURRENT_MACHINE_INDEX)

# Danh sách employee quét được từ QR
scanned_employees = []

def add_employee_from_qr(emp_info):
    # Debug: in ra id employee được add
    print(f"Thêm employee: id={emp_info.get('id')}, user_id={emp_info.get('user_id')}")
    # Kiểm tra trùng id, nếu chưa có thì thêm vào
    if not any(emp.get('id') == emp_info.get('id') for emp in scanned_employees):
        scanned_employees.append(emp_info)
        update_employee_listbox()
    else:
        print(f"Đã tồn tại employee id={emp_info.get('id')}")

def update_employee_listbox():
    employee_listbox.delete(0, tk.END)
    for emp in scanned_employees:
        employee_listbox.insert(tk.END, f"{emp['id']}: {emp['name']} ({emp.get('work_email', '')})")

def clear_scanned_employees():
    global scanned_employees, selected_workorder
    # Sử dụng công đoạn đã chọn
    if selected_workorder is None:
        messagebox.showerror("Lỗi", "Bạn chưa chọn công đoạn!")
        return
    # Lấy danh sách user_id từ scanned_employees
    user_ids = []
    for emp in scanned_employees:
        user_id = emp.get('user_id')
        if isinstance(user_id, list):
            user_id = user_id[0]
        if user_id:
            user_ids.append(user_id)
    if not user_ids:
        messagebox.showerror("Lỗi", "Không có user nào để điểm danh!")
        return
    # Gọi hàm thêm user vào workorder
    try:
        result = add_users_to_workorder(selected_workorder, user_ids)
        if result:
            messagebox.showinfo("Điểm danh nhân viên", "Đã thêm user vào công đoạn thành công!")
            workorder_text = ""
            for emp in scanned_employees:
                workorder_text += f"- {emp.get('id')}: {emp.get('name')} ({emp.get('work_email', '')})\n"
            if not workorder_text:
                workorder_text = "Không có nhân viên nào vừa điểm danh."
            scanned_employees.clear()
            update_employee_listbox()
            workorder_text_box.config(state=tk.NORMAL)
            workorder_text_box.delete(1.0, tk.END)
            workorder_text_box.insert(tk.END, workorder_text)
            workorder_text_box.config(state=tk.DISABLED)
            # Show countdown timer on the screen
            # Show countdown timer below 'Chi tiết lệnh sản xuất' using expected_duration_seconds
            show_countdown_timer_expected()
        else:
            messagebox.showerror("Lỗi", "Thêm user vào công đoạn thất bại!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Thêm user vào công đoạn thất bại: {e}")
    # Update 'Hoạt động & User' box with the list of employees just checked in
    

def update_timer(sec):
        if sec > 0:
            detail_text_box.countdown_label.config(text=f"Đếm ngược thời gian dự kiến: \n {sec} giây")
            detail_text_box.after(1000, update_timer, sec-1)
        else:
            detail_text_box.countdown_label.config(text="")

def show_countdown_timer_expected():
    # Show countdown timer below 'Chi tiết lệnh sản xuất' using expected_duration_seconds
    global expected_duration_seconds, countdown_text_box, actual_qty_entry, finish_step_btn
    # Create a ScrolledText widget for countdown if not exists
    if 'countdown_text_box' not in globals() or countdown_text_box is None:
        countdown_text_box = scrolledtext.ScrolledText(detail_text_box.master, width=40, height=2, font=("Arial", 14, "bold"), fg="red", state=tk.DISABLED)
        countdown_text_box.pack(padx=10, pady=(0, 5))
    def update_timer(sec):
        countdown_text_box.config(state=tk.NORMAL)
        countdown_text_box.delete(1.0, tk.END)
        if sec > 0:
            countdown_text_box.insert(tk.END, f"Đếm ngược thời gian dự kiến: {sec} giây")
            countdown_text_box.config(state=tk.DISABLED)
            countdown_text_box.after(1000, update_timer, sec-1)
        else:
            countdown_text_box.insert(tk.END, "Hết thời gian dự kiến!")
            countdown_text_box.config(state=tk.DISABLED)
    update_timer(expected_duration_seconds if expected_duration_seconds > 0 else 5)

    # Add entry for 'Số lượng thực tế' and button 'Kết thúc công đoạn' if not exists
    if 'actual_qty_entry' not in globals() or actual_qty_entry is None:
        actual_qty_label = tk.Label(detail_text_box.master, text="Số lượng thực tế:", font=("Arial", 12))
        actual_qty_label.pack(padx=10, pady=(5, 0))
        actual_qty_entry = tk.Entry(detail_text_box.master, font=("Arial", 12), width=20)
        actual_qty_entry.pack(padx=10, pady=(0, 5))
    if 'byproduct_qty_entry' not in globals() or byproduct_qty_entry is None:
        byproduct_qty_label = tk.Label(detail_text_box.master, text="Phụ phẩm thực tế:", font=("Arial", 12))
        byproduct_qty_label.pack(padx=10, pady=(0, 0))
        byproduct_qty_entry = tk.Entry(detail_text_box.master, font=("Arial", 12), width=20)
        byproduct_qty_entry.pack(padx=10, pady=(0, 5))
    if 'finish_step_btn' not in globals() or finish_step_btn is None:
        finish_step_btn = tk.Button(detail_text_box.master, text="Kết thúc công đoạn", font=("Arial", 12, "bold"), bg="#27ae60", fg="white", command=on_finish_step)
        finish_step_btn.pack(padx=10, pady=(0, 10))

def on_finish_step():
    actual_qty = actual_qty_entry.get() if 'actual_qty_entry' in globals() else None
    byproduct_qty = byproduct_qty_entry.get() if 'byproduct_qty_entry' in globals() else None
    # Calculate waste quantity
    estimated_qty = None
    if 'selected_workorder' in globals() and selected_workorder:
        try:
            estimated_qty = float(selected_workorder.get('qty_produced', 0))
        except Exception:
            estimated_qty = 0
    try:
        actual_qty_val = float(actual_qty) if actual_qty else 0
    except Exception:
        actual_qty_val = 0
    try:
        byproduct_qty_val = float(byproduct_qty) if byproduct_qty else 0
    except Exception:
        byproduct_qty_val = 0
    waste_qty = estimated_qty - actual_qty_val - byproduct_qty_val if estimated_qty is not None else None
    message = f"Số lượng thực tế: {actual_qty}\nPhụ phẩm thực tế: {byproduct_qty}"
    if waste_qty is not None:
        message += f"\nSố lượng phế phẩm: {waste_qty}"
    messagebox.showinfo("Kết thúc công đoạn", message)
    # TODO: Add logic to update workorder with actual_qty, byproduct_qty, waste_qty if needed
# def show_countdown_timer(seconds):
#     # Create or update a label for countdown timer
#     if not hasattr(root, 'countdown_label'):
#         root.countdown_label = tk.Label(root, text="", font=("Arial", 16, "bold"), fg="red")
#         root.countdown_label.pack(pady=(5, 0))
#     def update_timer(sec):
#         if sec > 0:
#             root.countdown_label.config(text=f"Đếm ngược: {sec} giây")
#             root.after(1000, update_timer, sec-1)
#         else:
#             root.countdown_label.config(text="")
#     update_timer(seconds)

def on_export_employees_qr():
    from tkinter import messagebox
    try:
        export_all_employees_with_qr(output_dir="QR")
        messagebox.showinfo("Xuất QR", "Đã xuất QR và thông tin nhân viên vào thư mục QR/")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Xuất QR thất bại: {e}")

root = tk.Tk()
root.title("Quet QR tu Camera")

# Thay đổi layout: chia 3 cột
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

left_panel = tk.Frame(main_frame)
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

center_panel = tk.Frame(main_frame, width=350)
center_panel.pack(side=tk.LEFT, fill=tk.Y)

right_panel = tk.Frame(main_frame, width=350)
right_panel.pack(side=tk.LEFT, fill=tk.Y)

# Panel trái chia 2 phần: trên là chi tiết, dưới là hoạt động
upper_left = tk.Frame(left_panel)
upper_left.pack(fill=tk.BOTH, expand=True)
lower_left = tk.Frame(left_panel)
lower_left.pack(fill=tk.BOTH, expand=True)

btn = tk.Button(upper_left, text="Quet QR", command=start_scan)
btn.pack(pady=10)

qr_text_box = scrolledtext.ScrolledText(upper_left, width=40, height=5)
qr_text_box.pack(padx=10, pady=10)

# Thông tin chi tiết lệnh sản xuất
label_detail = tk.Label(upper_left, text="Chi tiết lệnh sản xuất:", font=("Arial", 12, "bold"))
label_detail.pack(pady=(10, 0))
detail_text_box = scrolledtext.ScrolledText(upper_left, width=40, height=8, state=tk.DISABLED)
detail_text_box.pack(padx=10, pady=5)

# Danh sách hoạt động và user
label_wo = tk.Label(lower_left, text="Hoạt động & User:", font=("Arial", 12, "bold"))
label_wo.pack(pady=(10, 0))
workorder_text_box = scrolledtext.ScrolledText(lower_left, width=40, height=12, state=tk.DISABLED)
workorder_text_box.pack(padx=10, pady=5)


# Tiêu đề cho sơ đồ vị trí máy
machine_map_title = tk.Label(center_panel, text="Sơ đồ vị trí đặt máy", font=("Arial", 12, "bold"))
machine_map_title.pack(pady=(10, 0))

# Frame bản đồ máy (map tổng quát)
machine_map_frame = tk.Frame(center_panel)
machine_map_frame.pack(pady=(0, 10))

NUM_MACHINES = 10  # Số lượng máy tổng (có thể lấy động từ DB)
MACHINES_PER_ROW = 5
CURRENT_MACHINE_INDEX = None  # Index máy hiện tại (0-based), None nếu chưa chọn

machine_buttons = []  # Lưu các button để cập nhật màu

def render_machine_map(workcenters=None, current_idx=None):
    for widget in machine_map_frame.winfo_children():
        widget.destroy()
    global machine_buttons
    machine_buttons = []
    if workcenters is None:
        names = [f"Máy {i+1}" for i in range(NUM_MACHINES)]
    else:
        names = [wc.get('name', f"Máy {i+1}") for i, wc in enumerate(workcenters)]
    if current_idx is None:
        idx = CURRENT_MACHINE_INDEX
    else:
        idx = current_idx
    for i, name in enumerate(names):
        row = i // MACHINES_PER_ROW
        col = i % MACHINES_PER_ROW
        frame = tk.Frame(machine_map_frame)
        frame.grid(row=row*2, column=col, padx=10, pady=5)
        if idx is not None and i == idx:
            color = "#27ae60"
        else:
            color = "white"
        btn = tk.Label(frame, width=10, height=3, bg=color, relief=tk.RAISED, borderwidth=2)
        btn.pack()
        machine_buttons.append(btn)
        label = tk.Label(machine_map_frame, text=name, font=("Arial", 9))
        label.grid(row=row*2+1, column=col)

# Hiển thị map lần đầu
render_machine_map()

wc_label = tk.Label(center_panel, text="Danh sách máy:", font=("Arial", 12, "bold"))
wc_label.pack(pady=(10, 0))

wc_listbox = tk.Listbox(center_panel, width=40)
wc_listbox.pack(padx=10, pady=5, fill=tk.BOTH)
wc_listbox.bind('<<ListboxSelect>>', on_wc_select)  # chỉ bind 1 lần


# Khi ấn nút, vừa load danh sách máy vừa cập nhật lại bản đồ máy
def load_wc_and_render_map():
    load_workcenter_list()
    workcenters = getattr(wc_listbox, 'workcenters', None)
    render_machine_map(workcenters, CURRENT_MACHINE_INDEX)

load_wc_btn = tk.Button(center_panel, text="Tải danh sách vị trí", command=load_wc_and_render_map)
load_wc_btn.pack(pady=(0, 10))

wc_detail_box = scrolledtext.ScrolledText(center_panel, width=40, height=8, state=tk.DISABLED)
wc_detail_box.pack(padx=10, pady=5)

wc_workorder_label = tk.Label(center_panel, text="Công đoạn tại vị trí này:", font=("Arial", 11, "bold"))
wc_workorder_label.pack(pady=(0, 0))

wc_workorder_listbox = tk.Listbox(center_panel, width=40, height=8)
wc_workorder_listbox.pack(padx=10, pady=5, fill=tk.BOTH)
wc_workorder_listbox.bind('<<ListboxSelect>>', on_wo_select)  # chỉ để lấy selection, không reload

# Thêm label hiển thị công đoạn đã chọn
selected_workorder = None  # Biến lưu công đoạn đã chọn
selected_workorder_var = tk.StringVar()
selected_workorder_label = tk.Label(center_panel, textvariable=selected_workorder_var, font=("Arial", 11, "bold"), fg="blue")
selected_workorder_label.pack(pady=(0, 5))



# Chuyển danh sách nhân viên đã quét sang right_panel
employee_label = tk.Label(right_panel, text="Danh sách nhân viên đã quét:", font=("Arial", 12, "bold"))
employee_label.pack(pady=(10, 0))
employee_listbox = tk.Listbox(right_panel, width=40)
employee_listbox.pack(padx=10, pady=5, fill=tk.BOTH)

# Thêm nút xuất QR vào right_panel (dưới employee_listbox)

export_qr_btn = tk.Button(right_panel, text="Xuất QR & Thông tin nhân viên", command=on_export_employees_qr)
export_qr_btn.pack(pady=(10, 5))

# Thêm nút điểm danh nhân viên
clear_emp_btn = tk.Button(right_panel, text="Điểm danh nhân viên", command=clear_scanned_employees, bg="tomato", fg="white")
clear_emp_btn.pack(pady=(0, 10))

root.mainloop()
