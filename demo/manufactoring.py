import tkinter as tk
from tkinter import scrolledtext
import cv2
from pyzbar import pyzbar
import threading
import sys
import json
sys.path.append("../lib")
from lib.realtendant import get_all_mrp_productions, get_mrp_production_detail, get_all_workcenters, get_workorders_by_workcenter, export_all_employees_with_qr

def scan_qr():
    cap = cv2.VideoCapture(0)
    found = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        decoded_objs = pyzbar.decode(frame)
        for obj in decoded_objs:
            qr_data = obj.data.decode("utf-8")
            qr_text_box.delete(1.0, tk.END)
            qr_text_box.insert(tk.END, qr_data)
            # Nếu QR là json có user_id thì lấy thông tin employee theo user_id
            try:
                data = json.loads(qr_data)
                print(data)
                if isinstance(data, dict) and 'user_id' in data:
                    user_id_val = data['user_id']
                    # Nếu user_id là list (kiểu [id, name]), lấy id
                    if isinstance(user_id_val, list):
                        user_id_val = user_id_val[0]
                        if user_id_val:
                            add_employee_from_qr(data)
        
            except Exception:
                pass
            found = True
            break
        if found:
            break
    cap.release()

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
        wc_workorder_box.config(state=tk.NORMAL)
        wc_workorder_box.delete(1.0, tk.END)
        wc_workorder_box.config(state=tk.DISABLED)

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

def on_wc_select(event):
    selection = wc_listbox.curselection()
    # Nếu không có workcenter nào hoặc không chọn thì để trắng cả 2 box
    if not getattr(wc_listbox, 'workcenters', None) or not wc_listbox.workcenters:
        wc_detail_box.config(state=tk.NORMAL)
        wc_detail_box.delete(1.0, tk.END)
        wc_detail_box.config(state=tk.DISABLED)
        wc_workorder_box.config(state=tk.NORMAL)
        wc_workorder_box.delete(1.0, tk.END)
        wc_workorder_box.config(state=tk.DISABLED)
        return
    if not selection:
        wc_detail_box.config(state=tk.NORMAL)
        wc_detail_box.delete(1.0, tk.END)
        wc_detail_box.config(state=tk.DISABLED)
        wc_workorder_box.config(state=tk.NORMAL)
        wc_workorder_box.delete(1.0, tk.END)
        wc_workorder_box.config(state=tk.DISABLED)
        return
    idx = selection[0]
    wc = wc_listbox.workcenters[idx]
    wc_detail = f"ID: {wc.get('id')}\nTên: {wc.get('name')}\nMã: {wc.get('code')}\nCông ty: {wc.get('company_id')}\nHoạt động: {'Có' if wc.get('active') else 'Không'}\n"
    wc_detail_box.config(state=tk.NORMAL)
    wc_detail_box.delete(1.0, tk.END)
    wc_detail_box.insert(tk.END, wc_detail)
    wc_detail_box.config(state=tk.DISABLED)
    # Hiển thị danh sách workorder trên workcenter
    workorders = get_workorders_by_workcenter(wc.get('id'))
    workorder_text = ""
    for wo in workorders:
        workorder_text += f"- {wo.get('name')} (Trạng thái: {wo.get('state')})\n"
    wc_workorder_box.config(state=tk.NORMAL)
    wc_workorder_box.delete(1.0, tk.END)
    wc_workorder_box.insert(tk.END, workorder_text)
    wc_workorder_box.config(state=tk.DISABLED)

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

# Chuyển các widget danh sách lệnh sản xuất, vị trí sản xuất, workcenter detail, workorder sang center_panel
mrp_label = tk.Label(center_panel, text="Danh sách lệnh sản xuất:", font=("Arial", 12, "bold"))
mrp_label.pack(pady=(10, 0))

mrp_listbox = tk.Listbox(center_panel, width=40)
mrp_listbox.pack(padx=10, pady=5, fill=tk.BOTH)
mrp_listbox.bind('<<ListboxSelect>>', on_mrp_select)

load_btn = tk.Button(center_panel, text="Tải danh sách lệnh sản xuất", command=load_mrp_list)
load_btn.pack(pady=(0, 10))

wc_label = tk.Label(center_panel, text="Danh sách vị trí sản xuất:", font=("Arial", 12, "bold"))
wc_label.pack(pady=(10, 0))

wc_listbox = tk.Listbox(center_panel, width=40)
wc_listbox.pack(padx=10, pady=5, fill=tk.BOTH)
wc_listbox.bind('<<ListboxSelect>>', on_wc_select)

load_wc_btn = tk.Button(center_panel, text="Tải danh sách vị trí", command=load_workcenter_list)
load_wc_btn.pack(pady=(0, 10))

wc_detail_box = scrolledtext.ScrolledText(center_panel, width=40, height=8, state=tk.DISABLED)
wc_detail_box.pack(padx=10, pady=5)

wc_workorder_label = tk.Label(center_panel, text="Công đoạn tại vị trí này:", font=("Arial", 11, "bold"))
wc_workorder_label.pack(pady=(0, 0))
wc_workorder_box = scrolledtext.ScrolledText(center_panel, width=40, height=8, state=tk.DISABLED)
wc_workorder_box.pack(padx=10, pady=5)

# Chuyển danh sách nhân viên đã quét sang right_panel
employee_label = tk.Label(right_panel, text="Danh sách nhân viên đã quét:", font=("Arial", 12, "bold"))
employee_label.pack(pady=(10, 0))
employee_listbox = tk.Listbox(right_panel, width=40)
employee_listbox.pack(padx=10, pady=5, fill=tk.BOTH)

# Thêm nút xuất QR vào right_panel (dưới employee_listbox)
export_qr_btn = tk.Button(right_panel, text="Xuất QR & Thông tin nhân viên", command=on_export_employees_qr)
export_qr_btn.pack(pady=(10, 10))

root.mainloop()
