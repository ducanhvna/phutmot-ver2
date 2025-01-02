from django import forms


class TaskForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    project = forms.ChoiceField(
        label="Project", choices=[]
    )  # Sẽ được cập nhật trong view
    stage = forms.CharField(label="Stage", max_length=100)
    start_date = forms.DateTimeField(label="Start Date")
    deadline = forms.DateTimeField(label="Deadline")
