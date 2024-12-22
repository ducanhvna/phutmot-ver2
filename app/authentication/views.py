# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
import xmlrpc.client
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EmployeeSerializer

ODOO_URL = "http://odoo17:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get("username")
            # raw_password = form.cleaned_data.get("password1")
            # user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


class EmployeeListCreateAPIView(APIView):
    def get(self, request):
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
            employees = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'search_read',
                [[]], {'fields': ['id', 'name', 'job_id', 'department_id', 'code']}
            )
            serializer = EmployeeSerializer(employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Failed to authenticate with Odoo"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
            uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
            if uid:
                models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
                employee_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'create',
                    [{
                        'name': serializer.validated_data['name'],
                        'job_id': serializer.validated_data['job_id'],
                        'department_id': serializer.validated_data['department_id'],
                        'code': serializer.validated_data['code'],
                    }]
                )
                return Response({"id": employee_id}, status=status.HTTP_201_CREATED)
            return Response({"error": "Failed to authenticate with Odoo"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDetailAPIView(APIView):
    def get_employee(self, uid, employee_id):
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        employees = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'search_read',
            [[['id', '=', employee_id]]], {'fields': ['id', 'name', 'job_id', 'department_id', 'code']}
        )
        return employees[0] if employees else None

    def get(self, request, employee_id):
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if uid:
            employee = self.get_employee(uid, employee_id)
            if employee:
                serializer = EmployeeSerializer(employee)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Failed to authenticate with Odoo"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, employee_id):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
            uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
            if uid:
                employee = self.get_employee(uid, employee_id)
                if employee:
                    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'write',
                        [[employee_id], {
                            'name': serializer.validated_data['name'],
                            'job_id': serializer.validated_data['job_id'],
                            'department_id': serializer.validated_data['department_id'],
                            'code': serializer.validated_data['code'],
                        }]
                    )
                    return Response({"message": "Employee updated successfully"}, status=status.HTTP_200_OK)
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Failed to authenticate with Odoo"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, employee_id):
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD, 'hr.employee', 'unlink',
                [[employee_id]]
            )
            return Response({"message": "Employee deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Failed to authenticate with Odoo"}, status=status.HTTP_400_BAD_REQUEST)
