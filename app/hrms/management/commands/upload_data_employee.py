from django.core.management.base import BaseCommand
from hrms.models import Employee
import xmlrpc.client


class Command(BaseCommand):
    help = 'Upload Employee and Contract data from Django to Odoo'

    def handle(self, *args, **kwargs):
        # Define your Odoo connection parameters
        url = 'https://admin.hinosoft.com'
        db = 'odoo'
        username = 'admin'
        password = 'admin'

        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Get all Employee records from Django
        employees = Employee.objects.all()

        # Upload Employee data to Odoo
        for employee in employees:
            self.upload_employee_to_odoo(models, db, uid, password, employee)

    def upload_employee_to_odoo(self, models, db, uid, password, employee):
        # Check if employee already exists in Odoo
        odoo_employee_ids = models.execute_kw(
            db,
            uid,
            password,
            "hr.employee",
            "search",
            [[["code", "=", employee.employee_code], ["company_id", "=", 1]]],
        )

        # Employee data to upload
        employee_data = {
            'name': employee.info.get('name'),
            # 'user_id': employee.info.get('user_id'),
            # 'employee_ho': employee.info.get('employee_ho'),
            # 'part_time_company_id': employee.info.get('part_time_company_id'),
            # 'part_time_department_id': employee.info.get('part_time_department_id'),
            # 'company_id': employee.info.get('company_id'),
            'company_id': 1,
            'code': employee.employee_code,
            # 'department_id': employee.info.get('department_id'),
            # 'time_keeping_code': employee.info.get('time_keeping_code'),
            # 'job_title': employee.info.get('job_title'),
            # 'probationary_contract_termination_date': employee.info.get('probationary_contract_termination_date'),
            # 'severance_day': employee.info.get('severance_day'),
            # 'workingday': employee.info.get('workingday'),
            # 'probationary_salary_rate': employee.info.get('probationary_salary_rate'),
            # 'resource_calendar_id': employee.info.get('resource_calendar_id'),
            # 'date_sign': employee.info.get('date_sign'),
            # 'level': employee.info.get('level'),
            # 'working_status': employee.info.get('working_status'),
            # 'write_date': employee.info.get('write_date'),
            'active': employee.info.get('active')
        }

        if odoo_employee_ids:
            # Update existing employee
            models.execute_kw(
                db, uid, password,
                'hr.employee', 'write',
                [odoo_employee_ids, employee_data]
            )
            print(f"Updated employee {employee.employee_code} in Odoo")
            # Upload related contracts
            self.upload_contracts_to_odoo(models, db, uid, password, employee, odoo_employee_ids)
        else:
            # Create new employee
            models.execute_kw(
                db, uid, password,
                'hr.employee', 'create',
                [employee_data]
            )
            print(f"Created employee {employee.employee_code} in Odoo")

    def upload_contracts_to_odoo(self, models, db, uid, password, employee, odoo_employee_ids):
        contracts = [c for c in employee.other_contracts if c]

        # Assuming contracts is a JSON field in Employee model
        if employee.main_contract:
            contracts.append(employee.main_contract)
        for odoo_employee_id in odoo_employee_ids:
            for contract in contracts:
                # Check if contract already exists in Odoo
                odoo_contract_id = models.execute_kw(
                    db,
                    uid,
                    password,
                    "hr.contract",
                    "search",
                    [
                        [
                            ["employee_id", "=", odoo_employee_id],
                            ["company_id", "=", 1],
                            ["date_start", "=", contract.get("date_start")],
                        ]
                    ],
                )

                # Contract data to upload
                contract_data = {
                    'company_id': 1,
                    'name': contract.get('name'),
                    # 'contract_type_id': contract.get('contract_type_id'),
                    # 'minutes_per_day': contract.get('minutes_per_day'),
                    # 'employee_code': employee.employee_code,
                    'employee_id': odoo_employee_id,
                    'date_end': contract.get('date_end'),
                    'date_start': contract.get('date_start'),
                    # 'date_sign': contract.get('date_sign'),
                    # 'salary_rate': contract.get('salary_rate'),
                    # 'state': contract.get('state'),
                    'active': contract.get('active'),
                    'wage': 500000,
                    # 'start_end_attendance': contract.get('start_end_attendance'),
                    'resource_calendar_id': 1,
                    # 'resource_calendar_id': contract.get('resource_calendar_id'),
                    # 'depend_on_shift_time': contract.get('depend_on_shift_time'),
                    # 'by_hue_shift': contract.get('by_hue_shift'),
                    # 'write_date': contract.get('write_date')
                }

                if odoo_contract_id:
                    # Update existing contract
                    models.execute_kw(
                        db, uid, password,
                        'hr.contract', 'write',
                        [odoo_contract_id, contract_data]
                    )
                    print(f"Updated contract for employee {employee.employee_code} in Odoo")
                else:
                    # Create new contract
                    models.execute_kw(
                        db, uid, password,
                        'hr.contract', 'create',
                        [contract_data]
                    )
                    print(f"Created contract for employee {employee.employee_code} in Odoo")
