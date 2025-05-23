from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from hrms.models import Employee, Scheduling
from datetime import date


class EmployeeWithSchedulingAPITestCase(APITestCase):
    def setUp(self):
        # Tạo dữ liệu mẫu cho Employee và Scheduling
        self.employee = Employee.objects.create(
            employee_code="EMP001",
            start_date=date(2024, 5, 1),
            end_date=date(2024, 5, 31),
            time_keeping_code="TKC001",
            info={"name": "Nguyễn Văn A", "full_name": "Nguyễn Văn A", "time_keeping_code": "TKC001", "code": "EMP001"}
        )
        Scheduling.objects.create(
            employee_code="EMP001",
            start_date=date(2024, 5, 1),
            end_date=date(2024, 5, 31),
            scheduling_records=[{"date": "2024-05-01", "shift_name": "Ca sáng"}]
        )

    def test_employee_with_scheduling_list(self):
        url = reverse('employee_with_scheduling_list')
        print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)
        # Kiểm tra dữ liệu trả về có trường scheduling
        self.assertIn('scheduling', response.data['results'][0])

    def test_employee_with_scheduling_filter(self):
        url = reverse('employee_with_scheduling_list')
        response = self.client.get(url, {'employee_code': 'EMP001'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(emp['employee_code'] == 'EMP001' for emp in response.data['results']))

# Create your tests here.
