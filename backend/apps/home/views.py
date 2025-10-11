# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageOps
from pyzbar.pyzbar import decode as zbar_decode
import base64, io, os, uuid


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def scan_qr_view(request):
    # Đường dẫn WebSocket mà client sẽ kết nối
    ws_url = "ws://" + request.get_host() + "/ws/qr/"
    
    context = {
        'websocket_url': ws_url,
    }
    # Hiển thị template HTML của giao diện quét
    return render(request, 'qr/scan.html', context)

def qr_scanned(request):
    qr_data = request.GET.get('q', 'No data') 
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "qr_pad",
        {
            "type": "qr_message",
            "message": qr_data
        }
    )
    return JsonResponse({'status': 'sent', 'data': qr_data})

@csrf_exempt
def decode_image(request):
    if request.method != "POST":
        return JsonResponse({"error":"POST required"}, status=405)
    try:
        import json
        body = json.loads(request.body.decode('utf-8'))
        dataurl = body.get('image')
        if not dataurl:
            return JsonResponse({"error":"no image"}, status=400)

        header, b64 = dataurl.split(',', 1)
        image_data = base64.b64decode(b64)
        img = Image.open(io.BytesIO(image_data)).convert('RGB')

        # optional: increase contrast / convert to grayscale for better decode
        gray = ImageOps.grayscale(img)
        # Save debug file
        outdir = os.path.join(settings.MEDIA_ROOT, 'debug_frames')
        os.makedirs(outdir, exist_ok=True)
        fname = f"frame_{uuid.uuid4().hex[:8]}.jpg"
        fpath = os.path.join(outdir, fname)
        gray.save(fpath, format='JPEG', quality=90)

        results = []
        decoded = zbar_decode(gray)
        for d in decoded:
            results.append({
                "data": d.data.decode('utf-8', errors='ignore'),
                "type": d.type
            })

        return JsonResponse({"results": results, "debug_image": settings.MEDIA_URL + 'debug_frames/' + fname})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
