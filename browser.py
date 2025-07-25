# proxy_server.py
from flask import Flask, request, Response
import requests
import streamlit as st

app = Flask(__name__)

@app.route('/vnc/<path:path>')
def proxy_vnc(path):
    # 代理VNC请求
    vnc_host = "localhost:6080"
    url = f"http://{vnc_host}/{path}"
    
    resp = requests.get(url, params=request.args, stream=True)
    
    return Response(
        resp.iter_content(chunk_size=1024),
        content_type=resp.headers.get('content-type'),
        status=resp.status_code
    )

if __name__ == '__main__':
    app.run(port=8081)
