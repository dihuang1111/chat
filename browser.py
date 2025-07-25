import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from urllib.parse import quote, urlencode

def create_novnc_viewer():
    """创建一个纯前端的noVNC查看器"""
    
    novnc_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>noVNC Browser</title>
        <meta charset="utf-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.4.0/lib/util/logging.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.4.0/core/util/base64.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.4.0/core/websock.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.4.0/core/rfb.js"></script>
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #1e1e1e;
                font-family: Arial, sans-serif;
                color: white;
            }
            
            .container {
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            
            .toolbar {
                background: #333;
                padding: 10px;
                display: flex;
                gap: 10px;
                align-items: center;
                flex-wrap: wrap;
            }
            
            .input-group {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            input, select, button {
                padding: 5px 10px;
                border: 1px solid #555;
                background: #444;
                color: white;
                border-radius: 3px;
            }
            
            button {
                cursor: pointer;
                background: #0066cc;
            }
            
            button:hover {
                background: #0088ff;
            }
            
            button:disabled {
                background: #666;
                cursor: not-allowed;
            }
            
            .status {
                margin-left: auto;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
            }
            
            .status.disconnected { background: #dc3545; }
            .status.connecting { background: #ffc107; color: black; }
            .status.connected { background: #28a745; }
            
            #vnc-screen {
                flex: 1;
                background: #000;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
                overflow: hidden;
            }
            
            #vnc-canvas {
                border: 1px solid #555;
                max-width: 100%;
                max-height: 100%;
            }
            
            .message {
                color: #ccc;
                text-align: center;
                font-size: 18px;
            }
            
            .error {
                color: #ff6b6b;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="toolbar">
                <div class="input-group">
                    <label>Host:</label>
                    <input type="text" id="host" value="localhost" placeholder="VNC Host">
                </div>
                
                <div class="input-group">
                    <label>Port:</label>
                    <input type="number" id="port" value="5901" min="1" max="65535">
                </div>
                
                <div class="input-group">
                    <label>Password:</label>
                    <input type="password" id="password" placeholder="VNC Password">
                </div>
                
                <div class="input-group">
                    <label>Quality:</label>
                    <select id="quality">
                        <option value="0">Lossless</option>
                        <option value="6" selected>Medium</option>
                        <option value="9">Low</option>
                    </select>
                </div>
                
                <button id="connect-btn" onclick="toggleConnection()">Connect</button>
                <button onclick="sendCtrlAltDel()">Ctrl+Alt+Del</button>
                <button onclick="toggleFullscreen()">Fullscreen</button>
                
                <div class="status disconnected" id="status">Disconnected</div>
            </div>
            
            <div id="vnc-screen">
                <div class="message" id="message">Enter connection details and click Connect</div>
                <canvas id="vnc-canvas" style="display: none;"></canvas>
            </div>
        </div>

        <script>
            let rfb = null;
            let connected = false;

            function updateStatus(text, className) {
                const status = document.getElementById('status');
                status.textContent = text;
                status.className = 'status ' + className;
            }

            function showMessage(text, isError = false) {
                const message = document.getElementById('message');
                const canvas = document.getElementById('vnc-canvas');
                
                message.textContent = text;
                message.className = isError ? 'message error' : 'message';
                message.style.display = 'block';
                canvas.style.display = 'none';
            }

            function hideMessage() {
                const message = document.getElementById('message');
                const canvas = document.getElementById('vnc-canvas');
                
                message.style.display = 'none';
                canvas.style.display = 'block';
            }

            function toggleConnection() {
                if (connected) {
                    disconnect();
                } else {
                    connect();
                }
            }

            function connect() {
                const host = document.getElementById('host').value;
                const port = document.getElementById('port').value;
                const password = document.getElementById('password').value;
                const quality = document.getElementById('quality').value;

                if (!host || !port) {
                    showMessage('Please enter host and port', true);
                    return;
                }

                try {
                    // 构建WebSocket URL
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${host}:${port}`;
                    
                    showMessage('Connecting...');
                    updateStatus('Connecting...', 'connecting');

                    rfb = new RFB(document.getElementById('vnc-canvas'), wsUrl, {
                        credentials: { password: password },
                        repeaterID: '',
                        shared: true,
                        qualityLevel: parseInt(quality)
                    });

                    rfb.addEventListener('connect', () => {
                        connected = true;
                        document.getElementById('connect-btn').textContent = 'Disconnect';
                        updateStatus('Connected', 'connected');
                        hideMessage();
                    });

                    rfb.addEventListener('disconnect', (e) => {
                        connected = false;
                        document.getElementById('connect-btn').textContent = 'Connect';
                        updateStatus('Disconnected', 'disconnected');
                        
                        if (e.detail.clean) {
                            showMessage('Disconnected');
                        } else {
                            showMessage('Connection failed: ' + e.detail.reason, true);
                        }
                    });

                    rfb.addEventListener('credentialsrequired', () => {
                        showMessage('Authentication required - please check password', true);
                    });

                    rfb.addEventListener('securityfailure', (e) => {
                        showMessage('Security failure: ' + e.detail.reason, true);
                    });

                } catch (err) {
                    showMessage('Connection error: ' + err.message, true);
                    updateStatus('Error', 'disconnected');
                }
            }

            function disconnect() {
                if (rfb) {
                    rfb.disconnect();
                    rfb = null;
                }
            }

            function sendCtrlAltDel() {
                if (rfb && connected) {
                    rfb.sendCtrlAltDel();
                }
            }

            function toggleFullscreen() {
                const screen = document.getElementById('vnc-screen');
                if (document.fullscreenElement) {
                    document.exitFullscreen();
                } else {
                    screen.requestFullscreen();
                }
            }

            // 键盘快捷键
            document.addEventListener('keydown', function(e) {
                if (connected && rfb) {
                    // 阻止某些浏览器快捷键
                    if (e.ctrlKey && (e.key === 'w' || e.key === 't' || e.key === 'r')) {
                        e.preventDefault();
                    }
                }
            });

            // 窗口关闭前断开连接
            window.addEventListener('beforeunload', function() {
                if (rfb) {
                    rfb.disconnect();
                }
            });
        </script>
    </body>
    </html>
    """
    
    return novnc_html

def main():
    st.set_page_config(
        page_title="noVNC Browser", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🖥️ noVNC Browser")
    
    # 显示说明
    with st.expander("📋 使用说明"):
        st.markdown("""
        ### 这是一个纯Web的VNC客户端
        
        **支持的连接方式：**
        - 直接连接到VNC服务器的WebSocket端口
        - 通过websockify代理连接传统VNC服务器
        
        **使用步骤：**
        1. 确保目标VNC服务器支持WebSocket连接
        2. 在下方界面中输入连接信息
        3. 点击Connect按钮连接
        
        **常用端口：**
        - 5901: 传统VNC端口 (需要websockify代理)
        - 6080: 通常是noVNC/websockify的默认端口
        
        **设置websockify代理：**
        ```bash
        # 安装websockify
        pip install websockify
        
        # 启动代理 (将6080端口的WebSocket请求代理到5901的VNC)
        websockify 6080 localhost:5901
        ```
        """)
    
    # 连接预设
    st.subheader("🔗 快速连接")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**本地VNC + websockify**")
        st.code("Host: localhost\nPort: 6080")
        
    with col2:
        st.markdown("**Docker noVNC**")
        st.code("Host: localhost\nPort: 6080")
        st.caption("docker run -p 6080:6080 theasp/novnc")
        
    with col3:
        st.markdown("**远程VNC服务器**")
        st.code("Host: your-server.com\nPort: 6080")
    
    # 显示VNC客户端
    st.markdown("---")
    st.subheader("VNC 客户端")
    
    novnc_html = create_novnc_viewer()
    components.html(novnc_html, height=700, scrolling=False)
    
    # 故障排除
    with st.expander("🔧 故障排除"):
        st.markdown("""
        **常见问题及解决方案：**
        
        1. **Connection failed**: 
           - 检查VNC服务器是否运行
           - 确认端口号正确
           - 检查防火墙设置
        
        2. **WebSocket connection failed**:
           - 确保使用websockify代理
           - 检查是否支持WebSocket协议
        
        3. **Authentication failed**:
           - 检查密码是否正确
           - 某些VNC服务器不需要密码，留空即可
        
        4. **画面显示异常**:
           - 调整Quality设置
           - 检查网络连接稳定性
        
        **测试连接：**
        - 可以先用浏览器直接访问 http://host:port 查看是否有noVNC界面
        - 使用VNC客户端软件测试基础VNC连接
        """)

if __name__ == "__main__":
    main()
