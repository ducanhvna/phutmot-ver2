import os
from django.shortcuts import render, redirect, get_object_or_404
from .forms import DocumentForm
from .models import Document
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'credentials.json')


def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            file_path = document.file.path

            # Đẩy tệp lên Google Docs
            token_path = os.path.join(settings.BASE_DIR, 'documents/token.json')
            if not os.path.exists(token_path):
                return render(request, 'documents/error.html', {'message': 'Token file not found. Please authorize first.'})
            
            creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive.file'])
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


def document_detail(request, id):
    document = get_object_or_404(Document, id=id)
    return render(request, 'documents/document_detail.html', {'document': document})


def authorize(request):
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = request.build_absolute_uri('/documents/oauth2callback')
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return redirect(authorization_url)


def oauth2callback(request):
    state = request.session['state']
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = request.build_absolute_uri('/documents/oauth2callback')
    authorization_response = request.build_absolute_uri(request.get_full_path())
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    token_json = credentials.to_json()

    # Lưu token vào cơ sở dữ liệu hoặc tệp tin
    with open(os.path.join(settings.BASE_DIR, 'documents/token.json'), 'w') as token_file:
        token_file.write(token_json)

    return redirect('/documents/upload/')
