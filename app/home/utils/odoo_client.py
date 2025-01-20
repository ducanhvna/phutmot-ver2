import xmlrpc.client


class OdooClient:
    def __init__(self, base_url, db):
        self.base_url = base_url
        self.db = db
        self.common = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/common")
        self.uid = None

    def authenticate(self, username, password):
        try:
            self.uid = self.common.authenticate(self.db, username, password, {})
            if self.uid:
                self.password = password
                self.models = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/object")
                return {'status': 'success', 'user_id': self.uid}
            else:
                return {'status': 'fail', 'message': 'Invalid credentials'}
        except Exception as e:
            print(e)
            return {'status': 'error', 'message': str(e)}

    def get_employee_records(self, username):
        if self.uid is None or self.models is None:
            return {'status': 'error', 'message': 'User not authenticated'}

        try:
            # Get user ID associated with the username
            user_ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'res.users',
                'search',
                [[('login', '=', username)]]
            )
            if not user_ids:
                return {'status': 'fail', 'message': 'User not found'}
            user_id = user_ids[0]

            # Search for employees with the user_id matching found user_id
            employee_ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'hr.employee',
                'search',
                [[('user_id', '=', user_id)]]
            )
            if not employee_ids:
                return {'status': 'fail', 'message': 'Employee records not found'}

            # Read employee records, including the 'workingday' field
            employees = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'hr.employee',
                'read',
                [employee_ids],
                {'fields': ['name', 'code', 'job_id', 'department_id', 'company_id', 'workingday']}  # Add workingday field
            )

            # Sort employees by workingday and get the latest one
            latest_employee = sorted(employees, key=lambda x: x['workingday'], reverse=True)[0]

            # Fetch tasks assigned to the latest employee
            task_ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'project.task',
                'search',
                # ('user_ids', 'in', user_ids)
                [[]]
            )
            tasks = []
            if task_ids and len(task_ids) > 0:
                tasks = self.models.execute_kw(
                    self.db,
                    self.uid,
                    self.password,
                    'project.task',
                    'read',
                    [task_ids],
                    {'fields': ['name', 'id', 'date_deadline', 'priority', 'user_ids']}  # Add user_ids field
                )

            return {'status': 'success', 'data': {'employee': latest_employee, 'tasks': tasks}}
        except Exception as e:
            print(e)
            return {'status': 'error', 'message': str(e)}
