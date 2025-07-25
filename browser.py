import streamlit as st
import docker
import streamlit.components.v1 as components
import time

class NoVNCManager:
    def __init__(self):
        self.client = docker.from_env()
        self.container = None
    
    def start_vnc_container(self, image="dorowu/ubuntu-desktop-lxde-vnc:latest"):
        try:
            # 启动包含noVNC的容器
            self.container = self.client.containers.run(
                image,
                ports={'6080/tcp': 6080},
                detach=True,
                remove=True,
                environment={
                    'VNC_PASSWORD': 'password123',
                    'RESOLUTION': '1280x720'
                }
            )
            return True
        except Exception as e:
            st.error(f"Failed to start container: {e}")
            return False
    
    def stop_container(self):
        if self.container:
            self.container.stop()

def main():
    st.title("Streamlit noVNC Desktop")
    
    if 'vnc_manager' not in st.session_state:
        st.session_state.vnc_manager = NoVNCManager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Desktop"):
            with st.spinner("Starting virtual desktop..."):
                if st.session_state.vnc_manager.start_vnc_container():
                    time.sleep(5)  # 等待容器启动
                    st.success("Desktop started successfully!")
                    st.session_state.desktop_running = True
    
    with col2:
        if st.button("Stop Desktop"):
            st.session_state.vnc_manager.stop_container()
            st.session_state.desktop_running = False
            st.success("Desktop stopped")
    
    # 显示noVNC界面
    if st.session_state.get('desktop_running', False):
        st.subheader("Remote Desktop")
        components.iframe("http://localhost:6080/vnc.html?autoconnect=true", 
                         height=600, scrolling=True)

if __name__ == "__main__":
    main()
