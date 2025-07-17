import sys
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QMessageBox, 
                               QTableWidget, QTableWidgetItem, QGroupBox, QDateEdit,
                               QHeaderView, QFileDialog)
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QFont, QColor

# Import report functions
from TongHopBaoCao import (get_production_report, export_all_reports_to_excel, 
                          get_contract_summary_report, get_machine_summary_report,
                          get_salary_comparison_report)

class ReportGeneratorWorker(QThread):
    """Worker thread for generating reports to avoid UI blocking"""
    report_generated = Signal(list)
    excel_exported = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, operation, start_date, end_date, report_type="all"):
        super().__init__()
        self.operation = operation
        self.start_date = start_date
        self.end_date = end_date
        self.report_type = report_type
    
    def run(self):
        try:
            if self.operation == "generate":
                if self.report_type == "detail":
                    report_data = get_production_report(self.start_date, self.end_date)
                elif self.report_type == "contract":
                    report_data = get_contract_summary_report(self.start_date, self.end_date)
                elif self.report_type == "machine":
                    report_data = get_machine_summary_report(self.start_date, self.end_date)
                elif self.report_type == "salary":
                    report_data = get_salary_comparison_report(self.start_date, self.end_date)
                else:
                    report_data = get_production_report(self.start_date, self.end_date)
                
                self.report_generated.emit(report_data)
                
            elif self.operation == "export":
                excel_file = export_all_reports_to_excel(self.start_date, self.end_date)
                if excel_file:
                    self.excel_exported.emit(excel_file)
                else:
                    self.error_occurred.emit("Không có dữ liệu để xuất báo cáo")
                    
        except Exception as e:
            self.error_occurred.emit(str(e))

class ProductionReportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Báo cáo sản xuất")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_report_data = []
        self.current_report_type = "detail"
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("BÁO CÁO SẢN XUẤT")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Date selection and controls
        controls_group = self.create_controls_section()
        main_layout.addWidget(controls_group)
        
        # Report type selection
        report_type_group = self.create_report_type_section()
        main_layout.addWidget(report_type_group)
        
        # Report table
        table_group = self.create_table_section()
        main_layout.addWidget(table_group)
    
    def create_controls_section(self):
        controls_group = QGroupBox("Điều khiển báo cáo")
        controls_layout = QVBoxLayout(controls_group)
        
        # Date selection
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("Từ ngày:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("Đến ngày:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        
        # Quick date button
        today_btn = QPushButton("Hôm nay")
        today_btn.clicked.connect(self.set_today)
        date_layout.addWidget(today_btn)
        
        date_layout.addStretch()
        controls_layout.addLayout(date_layout)
        
        # Generate and export buttons
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Tạo báo cáo")
        self.generate_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(self.generate_btn)
        
        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.clicked.connect(self.refresh_report)
        button_layout.addWidget(self.refresh_btn)
        
        self.export_excel_btn = QPushButton("Xuất Excel")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        button_layout.addWidget(self.export_excel_btn)
        
        button_layout.addStretch()
        controls_layout.addLayout(button_layout)
        
        return controls_group
    
    def create_report_type_section(self):
        type_group = QGroupBox("Loại báo cáo")
        type_layout = QHBoxLayout(type_group)
        
        self.detail_btn = QPushButton("Chi tiết sản xuất")
        self.detail_btn.setCheckable(True)
        self.detail_btn.setChecked(True)
        self.detail_btn.clicked.connect(lambda: self.set_report_type("detail"))
        type_layout.addWidget(self.detail_btn)
        
        self.contract_btn = QPushButton("Tổng hợp công khoán")
        self.contract_btn.setCheckable(True)
        self.contract_btn.clicked.connect(lambda: self.set_report_type("contract"))
        type_layout.addWidget(self.contract_btn)
        
        self.machine_btn = QPushButton("Báo cáo theo máy")
        self.machine_btn.setCheckable(True)
        self.machine_btn.clicked.connect(lambda: self.set_report_type("machine"))
        type_layout.addWidget(self.machine_btn)
        
        self.salary_btn = QPushButton("Đối chiếu công khoán với lương")
        self.salary_btn.setCheckable(True)
        self.salary_btn.clicked.connect(lambda: self.set_report_type("salary"))
        type_layout.addWidget(self.salary_btn)
        
        type_layout.addStretch()
        return type_group
    
    def create_table_section(self):
        table_group = QGroupBox("Kết quả báo cáo")
        table_layout = QVBoxLayout(table_group)
        
        # Status label
        self.status_label = QLabel("Chưa có dữ liệu báo cáo")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        table_layout.addWidget(self.status_label)
        
        # Report table
        self.report_table = QTableWidget(0, 9)
        self.setup_detail_table()
        table_layout.addWidget(self.report_table)
        
        return table_group
    
    def setup_detail_table(self):
        """Setup table for detail report"""
        headers = [
            "Ngày", "Nhân viên", "Mã NV", "Máy/Khu vực", "Công đoạn", 
            "Thời gian (h)", "Sản lượng", "Phế phẩm", "Trạng thái"
        ]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setSortingEnabled(True)
    
    def setup_contract_table(self):
        """Setup table for contract summary"""
        headers = ["Mã NV", "Tên nhân viên", "Số lần đổi máy", "Tổng giờ làm", "Tổng sản lượng", "Tiền công khoán"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setSortingEnabled(True)
    
    def setup_machine_table(self):
        """Setup table for machine summary"""
        headers = ["Tên máy", "Lượt chuyền đến", "Tổng giờ công", "Tổng sản lượng", "Hiệu suất (sp/giờ)"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setSortingEnabled(True)
    
    def setup_salary_table(self):
        """Setup table for salary comparison"""
        headers = ["Tên nhân viên", "Mã NV", "Giờ công khoán", "Giờ công chuẩn", "Lương khoán", "Lương thực nhận", "Chênh lệch"]
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setSortingEnabled(True)
    
    def set_today(self):
        """Set date range to today"""
        today = QDate.currentDate()
        self.start_date.setDate(today)
        self.end_date.setDate(today)
    
    def set_report_type(self, report_type):
        """Set active report type"""
        self.current_report_type = report_type
        
        # Update button states
        self.detail_btn.setChecked(report_type == "detail")
        self.contract_btn.setChecked(report_type == "contract")
        self.machine_btn.setChecked(report_type == "machine")
        self.salary_btn.setChecked(report_type == "salary")
        
        # Setup appropriate table
        if report_type == "detail":
            self.setup_detail_table()
        elif report_type == "contract":
            self.setup_contract_table()
        elif report_type == "machine":
            self.setup_machine_table()
        elif report_type == "salary":
            self.setup_salary_table()
        
        # Clear current data
        self.report_table.setRowCount(0)
        self.current_report_data = []
        self.status_label.setText("Chọn khoảng thời gian và nhấn 'Tạo báo cáo'")
    
    def generate_report(self):
        """Generate report based on selected type and date range"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        self.status_label.setText("Đang tạo báo cáo...")
        self.generate_btn.setEnabled(False)
        
        # Start worker thread
        self.worker = ReportGeneratorWorker("generate", start_date, end_date, self.current_report_type)
        self.worker.report_generated.connect(self.on_report_generated)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    def refresh_report(self):
        """Refresh current report"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            return
        self.generate_report()
    
    def on_report_generated(self, report_data):
        """Handle generated report data"""
        self.generate_btn.setEnabled(True)
        self.current_report_data = report_data
        
        if not report_data:
            self.status_label.setText("Không có dữ liệu trong khoảng thời gian đã chọn")
            self.report_table.setRowCount(0)
            return
        
        # Populate table based on report type
        self.populate_table(report_data)
        self.status_label.setText(f"Đã tải {len(report_data)} bản ghi")
    
    def populate_table(self, data):
        """Populate table with report data"""
        self.report_table.setRowCount(len(data))
        
        for row, record in enumerate(data):
            if self.current_report_type == "detail":
                self.populate_detail_row(row, record)
            elif self.current_report_type == "contract":
                self.populate_contract_row(row, record)
            elif self.current_report_type == "machine":
                self.populate_machine_row(row, record)
            elif self.current_report_type == "salary":
                self.populate_salary_row(row, record)
    
    def populate_detail_row(self, row, record):
        """Populate detail report row"""
        columns = [
            record.get('date', ''),
            record.get('employee_name', ''),
            record.get('employee_code', ''),
            record.get('workcenter', ''),
            record.get('operation', ''),
            str(record.get('hours', 0)),
            str(record.get('qty_produced', 0)),
            str(record.get('scrap_qty', 0)),
            record.get('state', '')
        ]
        
        for col, value in enumerate(columns):
            self.report_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def populate_contract_row(self, row, record):
        """Populate contract summary row"""
        columns = [
            record.get('employee_code', ''),
            record.get('employee_name', ''),
            str(record.get('machine_changes', 0)),
            str(round(record.get('total_hours', 0), 2)),
            str(record.get('total_output', 0)),
            f"{record.get('contract_payment', 0):,.0f} VNĐ"
        ]
        
        for col, value in enumerate(columns):
            self.report_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def populate_machine_row(self, row, record):
        """Populate machine summary row"""
        columns = [
            record.get('machine_name', ''),
            str(record.get('workorder_count', 0)),
            str(round(record.get('total_hours', 0), 1)),
            str(record.get('total_output', 0)),
            str(record.get('efficiency', 0))
        ]
        
        for col, value in enumerate(columns):
            self.report_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def populate_salary_row(self, row, record):
        """Populate salary comparison row"""
        columns = [
            record.get('employee_name', ''),
            record.get('employee_code', ''),
            str(round(record.get('contract_hours', 0), 1)),
            str(round(record.get('standard_hours', 0), 1)),
            f"{record.get('contract_salary', 0):,.0f}",
            f"{record.get('total_salary', 0):,.0f}",
            f"{record.get('difference', 0):+,.0f}"
        ]
        
        for col, value in enumerate(columns):
            item = QTableWidgetItem(str(value))
            # Màu sắc cho cột chênh lệch
            if col == 6:  # Cột chênh lệch
                diff_value = record.get('difference', 0)
                if diff_value > 0:
                    item.setBackground(QColor(144, 238, 144))  # Light green
                elif diff_value < 0:
                    item.setBackground(QColor(255, 182, 193))  # Light red
            self.report_table.setItem(row, col, item)
    
    def export_to_excel(self):
        """Export all reports to Excel"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        self.status_label.setText("Đang xuất Excel...")
        self.export_excel_btn.setEnabled(False)
        
        # Start worker thread for export
        self.export_worker = ReportGeneratorWorker("export", start_date, end_date)
        self.export_worker.excel_exported.connect(self.on_excel_exported)
        self.export_worker.error_occurred.connect(self.on_error)
        self.export_worker.start()
    
    def on_excel_exported(self, file_path):
        """Handle successful Excel export"""
        self.export_excel_btn.setEnabled(True)
        self.status_label.setText("Đã xuất Excel thành công")
        
        # Auto open Reports folder
        reports_dir = "Reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        reply = QMessageBox.question(
            self, 
            "Xuất Excel thành công", 
            f"Đã xuất báo cáo thành công!\n{file_path}\n\nBạn có muốn mở thư mục Reports không?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Open folder in file explorer
            if sys.platform == "win32":
                os.startfile(reports_dir)
            elif sys.platform == "darwin":
                os.system(f"open {reports_dir}")
            else:
                os.system(f"xdg-open {reports_dir}")
    
    def on_error(self, error_message):
        """Handle errors"""
        self.generate_btn.setEnabled(True)
        self.export_excel_btn.setEnabled(True)
        self.status_label.setText("Có lỗi xảy ra")
        QMessageBox.critical(self, "Lỗi", f"Lỗi: {error_message}")
    
    def apply_styles(self):
        """Apply modern styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:checked {
                background-color: #28a745;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
                gridline-color: #dee2e6;
                selection-background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
            QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QLabel {
                color: #495057;
            }
        """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Production Report System")
    
    window = ProductionReportApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
