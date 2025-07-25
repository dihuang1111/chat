import streamlit as st
import streamlit.components.v1 as components
import subprocess
import threading
import time
import requests

class VNCServer:
    def __init__(self):
        self.vnc_process = None
        self.novnc_process = None
    
    def start_vnc_server(self):
        # 启动VNC服务器 (需要安装tigervnc-standalone-server)
        vnc_cmd = ["vncserver", ":1", "-geometry", "1280x720", "-depth", "24"]
        self.vnc_process = subprocess.Popen(vnc_cmd)
        
        # 启动noVNC (需要下载noVNC)
        novnc_cmd = ["python", "-m", "websockify", "--web=/path/to/noVNC", "6080", "localhost:5901"]
        self.novnc_process = subprocess.Popen(novnc_cmd)
        
        return True
    
    def stop_servers(self):
        if self.vnc_process:
            self.vnc_process.terminate()
        if self.novnc_process:
            self.novnc_process.terminate()
    
    def is_running(self):
        try:
            response = requests.get("http://localhost:6080", timeout=2)
            return response.status_code == 200
        except:
            return False

def main():
    st.set_page_config(page_title="noVNC Browser", layout="wide")
    st.title("🖥️ Remote Desktop Browser")
    
    if 'vnc_server' not in st.session_state:
        st.session_state.vnc_server = VNCServer()
    
    # 控制面板
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Start VNC", type="primary"):
                with st.spinner("Starting VNC server..."):
                    if st.session_state.vnc_server.start_vnc_server():
                        time.sleep(3)
                        st.success("VNC server started!")
                        st.rerun()
        
        with col2:
            if st.button("⏹️ Stop VNC", type="secondary"):
                st.session_state.vnc_server.stop_servers()
                st.success("VNC server stopped!")
                st.rerun()
        
        with col3:
            status = "🟢 Running" if st.session_state.vnc_server.is_running() else "🔴 Stopped"
            st.write(f"Status: {status}")
    
    # 显示VNC界面
    if st.session_state.vnc_server.is_running():
        st.markdown("---")
        components.iframe(
            "http://localhost:6080/vnc.html?autoconnect=true&resize=scale",
            height=700,
            scrolling=False
        )
    else:
        st.info("Please start the VNC server to access the remote desktop")

if __name__ == "__main__":
    main()
