import streamlit as st
import webbrowser
import subprocess

st.title("noVNC Launcher")

col1, col2 = st.columns(2)

with col1:
    if st.button("启动本地VNC桌面"):
        # 启动Docker容器
        cmd = "docker run -d -p 6080:80 --name vnc-desktop dorowu/ubuntu-desktop-lxde-vnc"
        subprocess.run(cmd.split())
        st.success("VNC桌面已启动")

with col2:
    if st.button("在新窗口打开VNC"):
        webbrowser.open("http://localhost:6080")
        st.info("VNC界面已在新窗口打开")

# 显示连接信息
st.markdown("""
### 连接信息
- URL: http://localhost:6080
- 默认密码: (空)

如果iframe无法显示，请点击上方按钮在新窗口打开。
""")

# 尝试嵌入
st.markdown("---")
st.subheader("VNC界面 (如果无法显示，请使用新窗口)")

# 使用容器来控制iframe
container = st.container()
with container:
    st.components.v1.iframe("http://localhost:6080", height=600, scrolling=False)
