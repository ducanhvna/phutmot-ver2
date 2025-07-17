import sys
import json
import threading
import cv2
from pyzbar import pyzbar
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                               QListWidget, QTextEdit, QLineEdit, QFileDialog, 
                               QMessageBox, QFrame, QSplitter, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QGroupBox)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QPixmap

sys.path.append("../lib")
from lib.realtendant import (add_users_to_workorder, get_all_mrp_productions, 
                            get_mrp_production_detail, get_all_workcenters, 
                            get_workorders_by_workcenter, export_all_employees_with_qr, 
                            get_workorder_detail)

class QRScanWorker(QThread):
    scan_completed = Signal(list)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        image = cv2.imread(self.file_path)
        if image is None:
            self.scan_completed.emit([])
            return
        decoded_objs = pyzbar.decode(image)
        self.scan_completed.emit(decoded_objs)

class ManufacturingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manufacturing QR Scanner")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize variables
        self.scanned_employees = []
        self.selected_workorder = None
        self.expected_duration_seconds = 0
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_remaining = 0
        self.current_machine_index = None
        self.workcenters = []
        self.machine_buttons = []
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with 3 columns
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - QR scan and work order details
        left_panel = self.create_left_panel()
        
        # Center panel - Machine map and work center selection
        center_panel = self.create_center_panel()
        
        # Right panel - Employee list and controls
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(center_panel, 1)
        main_layout.addWidget(right_panel, 1)
    
    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # QR Scan section
        qr_group = QGroupBox("Thông tin nhân viên")
        qr_layout = QVBoxLayout(qr_group)
        
        self.scan_btn = QPushButton("Quét QR")
        self.scan_btn.clicked.connect(self.scan_qr)
        qr_layout.addWidget(self.scan_btn)
        
        # QR Info table
        self.qr_info_table = QTableWidget(0, 2)
        self.qr_info_table.horizontalHeader().setVisible(False)
        self.qr_info_table.verticalHeader().setVisible(False)
        self.qr_info_table.horizontalHeader().setStretchLastSection(True)
        self.qr_info_table.setVisible(False)
        qr_layout.addWidget(self.qr_info_table)
        
        left_layout.addWidget(qr_group)
        
        # Work order details section
        details_group = QGroupBox("Chi tiết lệnh sản xuất")
        details_layout = QVBoxLayout(details_group)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(200)
        details_layout.addWidget(self.detail_text)
        
        # Countdown timer
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        self.countdown_label.setVisible(False)
        details_layout.addWidget(self.countdown_label)
        
        # Product quantity table
        self.qty_table = QTableWidget(0, 4)
        self.qty_table.setHorizontalHeaderLabels(["Sản phẩm", "Dự kiến", "Thực tế", "Phế phẩm"])
        self.qty_table.horizontalHeader().setStretchLastSection(True)
        self.qty_table.setVisible(False)
        details_layout.addWidget(self.qty_table)
        
        # Finish step button
        self.finish_btn = QPushButton("Kết thúc công đoạn")
        self.finish_btn.clicked.connect(self.on_finish_step)
        self.finish_btn.setVisible(False)
        details_layout.addWidget(self.finish_btn)
        
        left_layout.addWidget(details_group)
        
        # Activities and users section
        activities_group = QGroupBox("Hoạt động & User")
        activities_layout = QVBoxLayout(activities_group)
        
        self.workorder_text = QTextEdit()
        self.workorder_text.setReadOnly(True)
        activities_layout.addWidget(self.workorder_text)
        
        left_layout.addWidget(activities_group)
        
        return left_widget
    
    def create_center_panel(self):
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # Machine map section
        map_group = QGroupBox("Sơ đồ vị trí đặt máy")
        map_layout = QVBoxLayout(map_group)
        
        self.machine_map_widget = QWidget()
        self.machine_map_layout = QGridLayout(self.machine_map_widget)
        map_layout.addWidget(self.machine_map_widget)
        
        center_layout.addWidget(map_group)
        
        # Machine list section
        machine_group = QGroupBox("Danh sách máy")
        machine_layout = QVBoxLayout(machine_group)
        
        self.load_machines_btn = QPushButton("Tải danh sách vị trí")
        self.load_machines_btn.clicked.connect(self.load_workcenter_list)
        machine_layout.addWidget(self.load_machines_btn)
        
        self.machine_list = QListWidget()
        self.machine_list.itemClicked.connect(self.on_machine_select)
        machine_layout.addWidget(self.machine_list)
        
        self.machine_detail_text = QTextEdit()
        self.machine_detail_text.setReadOnly(True)
        self.machine_detail_text.setMaximumHeight(150)
        machine_layout.addWidget(self.machine_detail_text)
        
        center_layout.addWidget(machine_group)
        
        # Work orders section
        workorder_group = QGroupBox("Lệnh sản xuất tại máy")
        workorder_layout = QVBoxLayout(workorder_group)
        
        self.workorder_list = QListWidget()
        self.workorder_list.itemClicked.connect(self.on_workorder_select)
        workorder_layout.addWidget(self.workorder_list)
        
        self.selected_workorder_label = QLabel("")
        self.selected_workorder_label.setStyleSheet("color: blue; font-weight: bold;")
        workorder_layout.addWidget(self.selected_workorder_label)
        
        center_layout.addWidget(workorder_group)
        
        return center_widget
    
    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Employee list section
        employee_group = QGroupBox("Danh sách nhân viên đã quét")
        employee_layout = QVBoxLayout(employee_group)
        
        self.employee_list = QListWidget()
        employee_layout.addWidget(self.employee_list)
        
        right_layout.addWidget(employee_group)
        
        # Control buttons
        self.report_app_btn = QPushButton("Mở ứng dụng báo cáo")
        self.report_app_btn.clicked.connect(self.open_report_app)
        right_layout.addWidget(self.report_app_btn)
        
        self.export_qr_btn = QPushButton("Xuất QR & Thông tin nhân viên")
        self.export_qr_btn.clicked.connect(self.export_employees_qr)
        right_layout.addWidget(self.export_qr_btn)
        
        self.attendance_btn = QPushButton("Điểm danh nhân viên")
        self.attendance_btn.clicked.connect(self.clear_scanned_employees)
        right_layout.addWidget(self.attendance_btn)
        
        return right_widget
    
    def apply_styles(self):
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # Set specific button colors
        self.attendance_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.finish_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
    
    def scan_qr(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Chọn ảnh QR", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if not file_path:
            QMessageBox.information(self, "Thông báo", "Bạn chưa chọn ảnh!")
            return
        
        # Start QR scanning in worker thread
        self.qr_worker = QRScanWorker(file_path)
        self.qr_worker.scan_completed.connect(self.on_qr_scan_completed)
        self.qr_worker.start()
    
    def on_qr_scan_completed(self, decoded_objs):
        # Clear previous QR info
        self.qr_info_table.setRowCount(0)
        self.qr_info_table.setVisible(False)
        
        if not decoded_objs:
            self.qr_info_table.setRowCount(1)
            self.qr_info_table.setItem(0, 0, QTableWidgetItem("Kết quả"))
            self.qr_info_table.setItem(0, 1, QTableWidgetItem("Không tìm thấy mã QR trong ảnh!"))
            self.qr_info_table.setVisible(True)
            return
        
        for obj in decoded_objs:
            qr_data = obj.data.decode("utf-8")
            try:
                data = json.loads(qr_data)
                if isinstance(data, dict):
                    department = data.get('department_id', '')
                    if isinstance(department, list):
                        department = department[-1]
                    
                    info_fields = [
                        ("Tên", data.get('name', '')),
                        ("Email", data.get('work_email', '')),
                        ("SĐT", data.get('work_phone', '')),
                        ("Chức vụ", data.get('job_title', '')),
                        ("Phòng ban", department)
                    ]
                    
                    self.qr_info_table.setRowCount(len(info_fields))
                    for i, (label, value) in enumerate(info_fields):
                        self.qr_info_table.setItem(i, 0, QTableWidgetItem(label))
                        self.qr_info_table.setItem(i, 1, QTableWidgetItem(str(value)))
                    
                    self.qr_info_table.setVisible(True)
                    
                    if 'user_id' in data:
                        user_id_val = data['user_id']
                        if isinstance(user_id_val, list):
                            user_id_val = user_id_val[0]
                        if user_id_val:
                            self.add_employee_from_qr(data)
                else:
                    self.qr_info_table.setRowCount(1)
                    self.qr_info_table.setItem(0, 0, QTableWidgetItem("QR Data"))
                    self.qr_info_table.setItem(0, 1, QTableWidgetItem(qr_data))
                    self.qr_info_table.setVisible(True)
            except Exception:
                self.qr_info_table.setRowCount(1)
                self.qr_info_table.setItem(0, 0, QTableWidgetItem("QR Data"))
                self.qr_info_table.setItem(0, 1, QTableWidgetItem(qr_data))
                self.qr_info_table.setVisible(True)
    
    def add_employee_from_qr(self, emp_info):
        print(f"Thêm employee: id={emp_info.get('id')}, user_id={emp_info.get('user_id')}")
        
        if not any(emp.get('id') == emp_info.get('id') for emp in self.scanned_employees):
            self.scanned_employees.append(emp_info)
            self.update_employee_list()
        else:
            print(f"Đã tồn tại employee id={emp_info.get('id')}")
    
    def update_employee_list(self):
        self.employee_list.clear()
        for emp in self.scanned_employees:
            self.employee_list.addItem(f"{emp['id']}: {emp['name']} ({emp.get('work_email', '')})")
    
    def load_workcenter_list(self):
        try:
            self.workcenters = get_all_workcenters(fields=["id", "name", "code", "active", "company_id", "display_name"])
            if len(self.workcenters) > 100:
                self.workcenters = self.workcenters[:100]
        except Exception as e:
            self.workcenters = []
        
        self.machine_list.clear()
        for wc in self.workcenters:
            self.machine_list.addItem(f"{wc['id']}: {wc['name']} ({wc.get('code', '')})")
        
        self.render_machine_map()
        
        if not self.workcenters:
            self.machine_detail_text.clear()
            self.workorder_list.clear()
    
    def render_machine_map(self):
        # Clear existing buttons
        for button in self.machine_buttons:
            button.deleteLater()
        self.machine_buttons.clear()
        
        # Clear layout
        for i in reversed(range(self.machine_map_layout.count())):
            self.machine_map_layout.itemAt(i).widget().setParent(None)
        
        machines_per_row = 5
        for i, wc in enumerate(self.workcenters[:10]):  # Limit to 10 machines for display
            row = i // machines_per_row
            col = i % machines_per_row
            
            button = QPushButton(wc.get('name', f'Máy {i+1}'))
            button.setFixedSize(80, 60)
            
            if self.current_machine_index == i:
                button.setStyleSheet("background-color: #27ae60; color: white;")
            else:
                button.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc;")
            
            self.machine_map_layout.addWidget(button, row, col)
            self.machine_buttons.append(button)
    
    def on_machine_select(self, item):
        self.current_machine_index = self.machine_list.row(item)
        
        if self.current_machine_index < len(self.workcenters):
            wc = self.workcenters[self.current_machine_index]
            
            detail_text = f"""ID: {wc.get('id')}
Tên: {wc.get('name')}
Mã: {wc.get('code')}
Công ty: {wc.get('company_id')}
Hoạt động: {'Có' if wc.get('active') else 'Không'}"""
            
            self.machine_detail_text.setText(detail_text)
            
            # Load work orders for this machine
            try:
                workorders = get_workorders_by_workcenter(wc.get('id'))
                self.workorder_list.clear()
                self.workorders = workorders
                
                for wo in workorders:
                    self.workorder_list.addItem(f"{wo.get('id')}: {wo.get('name')} (Trạng thái: {wo.get('state')})")
            except Exception as e:
                self.workorders = []
                self.workorder_list.clear()
            
            self.render_machine_map()
    
    def on_workorder_select(self, item):
        if not hasattr(self, 'workorders') or not self.workorders:
            return
        
        idx = self.workorder_list.row(item)
        if idx < len(self.workorders):
            wo = self.workorders[idx]
            self.selected_workorder = wo
            
            detail = f"Lệnh sản xuất đã chọn: {wo.get('id')}: {wo.get('name')} (Trạng thái: {wo.get('state')})"
            self.selected_workorder_label.setText(detail)
            
            try:
                detail_workorder = get_workorder_detail(workorder_id=wo.get('id'))
                self.expected_duration_seconds = int(float(detail_workorder.get('duration_expected', 0)) * 60)
            except Exception:
                self.expected_duration_seconds = 0
            
            # Fill work order details
            try:
                detail_text = f"""Tên: {detail_workorder.get('name', '')}
Máy thực hiện: {detail_workorder.get('workcenter_id', ['', ''])[-1]}
Sản phẩm: {detail_workorder.get('product_id', ['', ''])[-1]}
Số lượng ước tính: {detail_workorder.get('qty_produced', '')}
Thời lượng dự kiến: {detail_workorder.get('duration_expected', '')}
Trạng thái: {detail_workorder.get('state', '')}"""
                
                self.detail_text.setText(detail_text)
            except Exception:
                pass
    
    def clear_scanned_employees(self):
        if self.selected_workorder is None:
            QMessageBox.critical(self, "Lỗi", "Bạn chưa chọn công đoạn!")
            return
        
        user_ids = []
        for emp in self.scanned_employees:
            user_id = emp.get('user_id')
            if isinstance(user_id, list):
                user_id = user_id[0]
            if user_id:
                user_ids.append(user_id)
        
        if not user_ids:
            QMessageBox.critical(self, "Lỗi", "Không có user nào để điểm danh!")
            return
        
        try:
            result = add_users_to_workorder(self.selected_workorder, user_ids)
            if result:
                QMessageBox.information(self, "Điểm danh nhân viên", "Đã thêm user vào công đoạn thành công!")
                
                workorder_text = ""
                for emp in self.scanned_employees:
                    workorder_text += f"- {emp.get('id')}: {emp.get('name')} ({emp.get('work_email', '')})\n"
                
                if not workorder_text:
                    workorder_text = "Không có nhân viên nào vừa điểm danh."
                
                self.scanned_employees.clear()
                self.update_employee_list()
                self.workorder_text.setText(workorder_text)
                
                # Hide QR info and show countdown timer
                self.qr_info_table.setVisible(False)
                self.show_countdown_timer()
            else:
                QMessageBox.critical(self, "Lỗi", "Thêm user vào công đoạn thất bại!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Thêm user vào công đoạn thất bại: {e}")
    
    def show_countdown_timer(self):
        # Show countdown timer and quantity table
        self.countdown_remaining = self.expected_duration_seconds if self.expected_duration_seconds > 0 else 5
        self.countdown_label.setVisible(True)
        self.countdown_timer.start(1000)  # Update every second
        
        # Show quantity table
        self.qty_table.setRowCount(1)
        
        product_name = ""
        estimated_qty = 0
        if self.selected_workorder:
            product = self.selected_workorder.get('product_id', ['', ''])
            product_name = product[-1] if isinstance(product, list) else str(product)
            try:
                estimated_qty = float(self.selected_workorder.get('qty_produced', 0))
            except Exception:
                estimated_qty = 0
        
        self.qty_table.setItem(0, 0, QTableWidgetItem(product_name))
        self.qty_table.setItem(0, 1, QTableWidgetItem(str(estimated_qty)))
        
        # Add editable actual quantity cell
        actual_qty_item = QTableWidgetItem("")
        self.qty_table.setItem(0, 2, actual_qty_item)
        
        # Waste quantity (will be calculated)
        self.qty_table.setItem(0, 3, QTableWidgetItem(""))
        
        self.qty_table.setVisible(True)
        self.finish_btn.setVisible(True)
    
    def update_countdown(self):
        if self.countdown_remaining > 0:
            self.countdown_label.setText(f"Đếm ngược thời gian dự kiến: {self.countdown_remaining} giây")
            self.countdown_remaining -= 1
        else:
            self.countdown_label.setText("Hết thời gian dự kiến!")
            self.countdown_timer.stop()
    
    def on_finish_step(self):
        # Calculate waste quantity
        actual_qty_text = self.qty_table.item(0, 2).text() if self.qty_table.item(0, 2) else ""
        estimated_qty_text = self.qty_table.item(0, 1).text() if self.qty_table.item(0, 1) else "0"
        product_name = self.qty_table.item(0, 0).text() if self.qty_table.item(0, 0) else ""
        
        try:
            actual_qty = float(actual_qty_text) if actual_qty_text else 0
            estimated_qty = float(estimated_qty_text)
        except ValueError:
            actual_qty = 0
            estimated_qty = 0
        
        waste_qty = estimated_qty - actual_qty
        
        # Update waste column
        self.qty_table.setItem(0, 3, QTableWidgetItem(str(waste_qty)))
        
        # Show completion message
        message = f"""Sản phẩm: {product_name}
Dự kiến: {estimated_qty}
Thực tế: {actual_qty_text}
Phế phẩm: {waste_qty}"""
        
        QMessageBox.information(self, "Kết thúc công đoạn", message)
        
        # Reset UI
        self.reset_ui()
    
    def reset_ui(self):
        # Hide and clear countdown
        self.countdown_timer.stop()
        self.countdown_label.setVisible(False)
        self.countdown_label.setText("")
        
        # Hide quantity table and finish button
        self.qty_table.setVisible(False)
        self.qty_table.setRowCount(0)
        self.finish_btn.setVisible(False)
        
        # Clear text areas
        self.detail_text.clear()
        self.workorder_text.clear()
        
        # Clear employee list
        self.employee_list.clear()
        
        # Reset variables
        self.selected_workorder = None
        self.expected_duration_seconds = 0
        self.scanned_employees.clear()
        self.selected_workorder_label.setText("")
    
    def export_employees_qr(self):
        try:
            export_all_employees_with_qr(output_dir="QR")
            QMessageBox.information(self, "Xuất QR", "Đã xuất QR và thông tin nhân viên vào thư mục QR/")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Xuất QR thất bại: {e}")

    def open_report_app(self):
        """Open the production report application"""
        try:
            import subprocess
            import sys
            
            # Run the report app as a separate process
            subprocess.Popen([sys.executable, "ProductionReportApp.py"], 
                           cwd=".", creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            
            QMessageBox.information(self, "Ứng dụng báo cáo", "Đã mở ứng dụng báo cáo sản xuất!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở ứng dụng báo cáo: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Manufacturing QR Scanner")
    
    window = ManufacturingApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
