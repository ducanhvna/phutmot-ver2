import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import cv2
from pyzbar import pyzbar
import threading
import sys
import json
sys.path.append("../lib")
from lib.realtendant import add_users_to_workorder, get_all_mrp_productions, get_mrp_production_detail, get_all_workcenters, get_workorders_by_workcenter, export_all_employees_with_qr

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
    # Hiển thị chi tiết công đoạn lên UI
    detail = f"Công đoạn đã chọn: {wo.get('id')}: {wo.get('name')} (Trạng thái: {wo.get('state')})"
    selected_workorder_var.set(detail)

def on_wc_select(event):
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
        else:
            messagebox.showerror("Lỗi", "Thêm user vào công đoạn thất bại!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Thêm user vào công đoạn thất bại: {e}")
    scanned_employees.clear()
    update_employee_listbox()

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
wc_listbox.bind('<<ListboxSelect>>', on_wc_select)  # chỉ bind 1 lần

load_wc_btn = tk.Button(center_panel, text="Tải danh sách vị trí", command=load_workcenter_list)
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
