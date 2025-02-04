from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            file_path = document.file.path

            # Đẩy tệp lên Google Docs
            creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive.file'])
            service = build('drive', 'v3', credentials=creds)
            file_metadata = {'name': document.title}
            media = MediaFileUpload(file_path, mimetype='application/pdf')
            file = service.files().create(body=file_metadata, media_body=media, fields='webViewLink').execute()

            # Lưu liên kết Google Doc vào cơ sở dữ liệu
            document.google_doc_link = file.get('webViewLink')
            document.save()

            return redirect('document_detail', document.id)
    else:
        form = DocumentForm()
    return render(request, 'documents/upload.html', {'form': form})
