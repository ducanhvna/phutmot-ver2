from django.views import View
from django.shortcuts import render


class TaskCreateView(View):
    def get(self, request):
        return render(request, 'hrms/task_create.html')
