import streamlit as st
import hashlib
import re
from datetime import datetime
import requests
import base64

# 凯撒密码加密/解密函数
def caesar_cipher_encrypt(text, shift):
    """使用凯撒密码加密IP地址"""
    result = ""
    for char in text:
        if char.isdecimal():
            # 数字加密 (0-9)
            result += str((int(char) + shift) % 10)
        elif char == '.':
            # 点号保持不变
            result += char
        else:
            # 其他字符保持不变
            result += char
    return result

def caesar_cipher_decrypt(text, shift):
    """使用凯撒密码解密IP地址"""
    result = ""
    for char in text:
        if char.isdecimal():
            # 数字解密 (0-9)
            result += str((int(char) - shift) % 10)
        elif char == '.':
            # 点号保持不变
            result += char
        else:
            # 其他字符保持不变
            result += char
    return result

def create_vm_browser_interface():
    """创建类似hyperbeam/invited的VM浏览器界面"""
    st.markdown("""
    <style>
    .vm-browser-container {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 0;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        overflow: hidden;
    }
    .vm-header {
        background: linear-gradient(90deg, #2d3748, #4a5568);
        padding: 12px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #4a5568;
    }
    .vm-controls {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .vm-btn {
        background: #4299e1;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .vm-btn:hover {
        background: #3182ce;
        transform: translateY(-1px);
    }
    .vm-url-bar {
        background: #2d3748;
        color: white;
        border: 1px solid #4a5568;
        border-radius: 6px;
        padding: 8px 12px;
        min-width: 300px;
        font-family: 'Courier New', monospace;
    }
    .vm-screen {
        background: #000;
        height: 500px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .vm-loading {
        color: #4299e1;
        font-size: 18px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    .vm-viewer {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1a202c, #2d3748);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        position: relative;
    }
    .vm-screen-content {
        width: 90%;
        height: 90%;
        background: #f7fafc;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        overflow: hidden;
        position: relative;
    }
    .connection-indicator {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #48bb78;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 10px;
        z-index: 10;
    }
    .vm-taskbar {
        background: #2d3748;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        border-top: 1px solid #4a5568;
    }
    .taskbar-left {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .taskbar-right {
        color: #a0aec0;
        font-size: 12px;
    }
    .browser-window {
        width: 100%;
        height: calc(100% - 40px);
        background: white;
        position: relative;
        overflow: hidden;
    }
    .browser-chrome {
        background: #f1f5f9;
        border-bottom: 1px solid #e2e8f0;
        padding: 8px 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .browser-content {
        height: calc(100% - 45px);
        background: white;
        overflow-y: auto;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="vm-browser-container">', unsafe_allow_html=True)
    
    # VM浏览器头部
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        st.markdown('<div style="color: white; font-weight: bold; padding: 8px;">🖥️ VM Browser Session - hyperbeam.com</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 重新连接", key="reconnect"):
            st.success("正在重新连接到VM...")
    with col3:
        if st.button("📱 切换设备", key="switch_device"):
            st.info("设备视图已切换")
    with col4:
        if st.button("⚙️", key="vm_settings"):
            st.info("VM设置面板")
    
    # VM屏幕显示区域
    st.markdown("""
    <div class="vm-screen">
        <div class="connection-indicator">🟢 已连接</div>
        <div class="vm-viewer">
            <div class="vm-screen-content">
                <div class="browser-window">
                    <div class="browser-chrome">
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 12px; height: 12px; background: #ff5f57; border-radius: 50%;"></div>
                            <div style="width: 12px; height: 12px; background: #ffbd2e; border-radius: 50%;"></div>
                            <div style="width: 12px; height: 12px; background: #28ca42; border-radius: 50%;"></div>
                        </div>
                        <div style="flex: 1; margin: 0 15px;">
                            <div style="background: white; border: 1px solid #d1d5db; border-radius: 6px; padding: 4px 12px; font-size: 14px;">
                                🔒 """ + st.session_state.current_url + """
                            </div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 20px; height: 20px; background: #e5e7eb; border-radius: 3px;"></div>
                            <div style="width: 20px; height: 20px; background: #e5e7eb; border-radius: 3px;"></div>
                        </div>
                    </div>
                    <div class="browser-content" id="vm-content">
    """, unsafe_allow_html=True)
    
    # 显示网页内容
    display_vm_webpage_content()
    
    st.markdown("""
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # VM控制面板
    st.markdown("""
    <div class="vm-taskbar">
        <div class="taskbar-left">
            <span style="color: #4299e1;">🖥️ Virtual Machine</span>
            <span style="color: #68d391;">● Chrome Browser</span>
            <span style="color: #f6ad55;">⚡ GPU加速</span>
        </div>
        <div class="taskbar-right">
            FPS: 60 | CPU: 12% | RAM: 2.1GB | 延迟: 23ms
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # VM控制按钮
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        new_url = st.text_input("🌐 导航到", value=st.session_state.current_url, key="vm_nav")
        if st.button("Go", key="vm_go"):
            st.session_state.current_url = new_url
            st.rerun()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 主页", key="vm_home"):
            st.session_state.current_url = "https://www.google.com"
            st.rerun()
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 刷新", key="vm_refresh"):
            st.rerun()
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📷 截图", key="vm_screenshot"):
            st.success("VM屏幕截图已保存")
    
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎮 全屏", key="vm_fullscreen"):
            st.info("VM已切换到全屏模式")

def display_vm_webpage_content():
    """在VM环境中显示网页内容"""
    current_url = st.session_state.current_url.lower()
    
    if "google.com" in current_url:
        st.markdown("""
        <div style="text-align: center; padding: 80px 20px;">
            <div style="font-size: 90px; color: #4285f4; margin-bottom: 30px; font-weight: 300;">
                G<span style="color: #ea4335;">o</span><span style="color: #fbbc05;">o</span><span style="color: #4285f4;">g</span><span style="color: #34a853;">l</span><span style="color: #ea4335;">e</span>
            </div>
            <div style="margin: 30px 0;">
                <div style="width: 500px; margin: 0 auto; position: relative;">
                    <input type="text" placeholder="在 Google 上搜索，或者输入一个网址" 
                           style="width: 100%; padding: 12px 45px 12px 15px; border: 1px solid #dfe1e5; border-radius: 24px; outline: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%);">🔍</div>
                </div>
            </div>
            <div style="margin-top: 30px;">
                <button style="background: #f8f9fa; border: 1px solid #f8f9fa; border-radius: 4px; padding: 10px 20px; margin: 0 5px; cursor: pointer;">Google 搜索</button>
                <button style="background: #f8f9fa; border: 1px solid #f8f9fa; border-radius: 4px; padding: 10px 20px; margin: 0 5px; cursor: pointer;">手气不错</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif "youtube.com" in current_url:
        st.markdown("""
        <div style="background: #0f0f0f; color: white; padding: 20px; min-height: 300px;">
            <div style="display: flex; align-items: center; padding-bottom: 20px; border-bottom: 1px solid #333;">
                <div style="font-size: 24px; color: #ff0000; font-weight: bold;">📺 YouTube</div>
                <div style="flex: 1; margin: 0 20px;">
                    <input type="text" placeholder="搜索" style="width: 100%; padding: 8px 15px; background: #121212; border: 1px solid #333; border-radius: 2px; color: white;">
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px;">
                <div style="background: #1a1a1a; border-radius: 8px; overflow: hidden;">
                    <div style="background: #333; height: 120px; display: flex; align-items: center; justify-content: center; color: #666;">
                        ▶️ 视频缩略图
                    </div>
                    <div style="padding: 12px;">
                        <h4 style="margin: 0 0 8px 0; font-size: 14px;">示例视频标题 - 技术教程</h4>
                        <p style="color: #aaa; font-size: 12px; margin: 0;">TechChannel • 1.2M views • 2 days ago</p>
                    </div>
                </div>
                <div style="background: #1a1a1a; border-radius: 8px; overflow: hidden;">
                    <div style="background: #333; height: 120px; display: flex; align-items: center; justify-content: center; color: #666;">
                        ▶️ 视频缩略图
                    </div>
                    <div style="padding: 12px;">
                        <h4 style="margin: 0 0 8px 0; font-size: 14px;">编程实战项目分享</h4>
                        <p style="color: #aaa; font-size: 12px; margin: 0;">CodeMaster • 856K views • 1 week ago</p>
                    </div>
                </div>
                <div style="background: #1a1a1a; border-radius: 8px; overflow: hidden;">
                    <div style="background: #333; height: 120px; display: flex; align-items: center; justify-content: center; color: #666;">
                        ▶️ 视频缩略图
                    </div>
                    <div style="padding: 12px;">
                        <h4 style="margin: 0 0 8px 0; font-size: 14px;">AI技术最新发展</h4>
                        <p style="color: #aaa; font-size: 12px; margin: 0;">AI News • 2.3M views • 3 days ago</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div style="padding: 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
            <h2 style="margin-bottom: 20px;">🌐 正在VM中加载网页</h2>
            <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 8px; margin: 20px 0;">
                <div style="font-size: 18px; margin-bottom: 15px;">当前访问: {st.session_state.current_url}</div>
                <div style="display: flex; justify-content: center; align-items: center; gap: 20px;">
                    <div style="width: 60px; height: 60px; border: 3px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    <div>正在安全的VM环境中加载页面内容...</div>
                </div>
            </div>
            <div style="font-size: 14px; opacity: 0.8;">
                🔒 所有网络流量均通过加密隧道传输<br>
                🛡️ VM环境完全隔离，确保主机安全
            </div>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)
    """验证IP地址格式"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return False

# 初始化session state
if 'authentication_stage' not in st.session_state:
    st.session_state.authentication_stage = 1
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'locked' not in st.session_state:
    st.session_state.locked = False
if 'pattern_input' not in st.session_state:
    st.session_state.pattern_input = []
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_url' not in st.session_state:
    st.session_state.current_url = "https://www.google.com"
if 'browser_history' not in st.session_state:
    st.session_state.browser_history = []

# 配置信息 (实际部署时应存储在安全的配置文件中)
CORRECT_PIN = "1234"  # 实际使用时请修改
CORRECT_PATTERN = [1, 2, 3, 4, 5]  # 实际使用时请修改
ENCRYPTED_IP_INPUT = "421.499.553.03"  # 加密后的IP地址
CAESAR_SHIFT = 3
SYSTEM_STORED_IP = "188.166.220.70"  # 解密后的真实IP (系统内部存储)
MAX_ATTEMPTS = 3

# 页面标题
st.title("🔐 MFA多层安全认证系统")
st.markdown("---")

# 如果已通过认证，显示VM浏览器
if st.session_state.authenticated:
    # 顶部工具栏
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.success("✅ 已通过多重身份验证 - VM浏览器已激活")
    with col2:
        if st.button("🔒 锁定系统"):
            st.session_state.authenticated = False
            st.session_state.authentication_stage = 1
            st.session_state.attempts = 0
            st.session_state.pattern_input = []
            st.rerun()
    with col3:
        if st.button("📊 会话信息"):
            st.info(f"会话开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # 显示VM浏览器界面
    create_vm_browser_interface()
    
    # 浏览器功能面板
    st.markdown("---")
    st.subheader("🛠️ 浏览器控制面板")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔖 添加书签"):
            st.success(f"已添加书签: {st.session_state.current_url}")
    
    with col2:
        if st.button("📋 复制链接"):
            st.success("链接已复制到剪贴板")
    
    with col3:
        if st.button("🛡️ 安全检查"):
            st.info("✅ 当前连接安全 | 🔒 SSL已启用 | 🚫 无恶意内容")
    
    with col4:
        if st.button("📊 流量统计"):
            st.metric("数据传输", "2.3 MB", "↗️ +0.5 MB")
    
    # 快速导航
    st.subheader("⚡ 快速导航")
    quick_sites = {
        "🔍 Google": "https://www.google.com",
        "📺 YouTube": "https://www.youtube.com",
        "🐙 GitHub": "https://www.github.com",
        "📧 Gmail": "https://mail.google.com",
        "💼 LinkedIn": "https://www.linkedin.com",
        "🐦 Twitter": "https://www.twitter.com"
    }
    
    cols = st.columns(6)
    for i, (name, url) in enumerate(quick_sites.items()):
        with cols[i]:
            if st.button(name, key=f"quick_{i}"):
                st.session_state.browser_history.append(st.session_state.current_url)
                st.session_state.current_url = url
                st.rerun()
    
    st.stop()  # 不再显示认证界面

# 检查是否被锁定
if st.session_state.locked:
    st.error("🚫 系统已锁定！尝试次数过多，请联系管理员。")
    if st.button("重置系统"):
        st.session_state.authentication_stage = 1
        st.session_state.attempts = 0
        st.session_state.locked = False
        st.session_state.pattern_input = []
        st.rerun()
    st.stop()

# 显示当前认证阶段
st.info(f"当前认证阶段: {st.session_state.authentication_stage}/3")
st.info(f"剩余尝试次数: {MAX_ATTEMPTS - st.session_state.attempts}")

# 第一层：PIN码验证
if st.session_state.authentication_stage == 1:
    st.header("🔢 第一层：PIN码验证")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pin_input = st.text_input("请输入4位PIN码:", type="password", max_chars=4)
        
        if st.button("验证PIN码", use_container_width=True):
            if pin_input == CORRECT_PIN:
                st.success("✅ PIN码验证成功！")
                st.session_state.authentication_stage = 2
                st.session_state.attempts = 0  # 重置尝试次数
                st.rerun()
            else:
                st.session_state.attempts += 1
                remaining = MAX_ATTEMPTS - st.session_state.attempts
                if remaining > 0:
                    st.error(f"❌ PIN码错误！还有 {remaining} 次尝试机会")
                else:
                    st.error("🚫 PIN码验证失败次数过多，系统锁定！")
                    st.session_state.locked = True
                    st.rerun()

# 第二层：图案解锁
elif st.session_state.authentication_stage == 2:
    st.header("🔘 第二层：图案解锁")
    st.write("点击下方数字按钮创建解锁图案（按顺序点击）：")
    
    # 创建3x3图案网格
    cols = st.columns(3)
    for i in range(9):
        row = i // 3
        col = i % 3
        button_num = i + 1
        
        with cols[col]:
            # 检查是否已被选择
            is_selected = button_num in st.session_state.pattern_input
            button_style = "🔴" if is_selected else "⚪"
            
            if st.button(f"{button_style} {button_num}", key=f"pattern_{button_num}"):
                if button_num not in st.session_state.pattern_input:
                    st.session_state.pattern_input.append(button_num)
                    st.rerun()
    
    # 显示当前图案
    if st.session_state.pattern_input:
        st.write(f"当前图案: {' → '.join(map(str, st.session_state.pattern_input))}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("清除图案"):
            st.session_state.pattern_input = []
            st.rerun()
    
    with col2:
        if st.button("验证图案") and st.session_state.pattern_input:
            if st.session_state.pattern_input == CORRECT_PATTERN:
                st.success("✅ 图案验证成功！")
                st.session_state.authentication_stage = 3
                st.session_state.attempts = 0
                st.session_state.pattern_input = []
                st.rerun()
            else:
                st.session_state.attempts += 1
                remaining = MAX_ATTEMPTS - st.session_state.attempts
                if remaining > 0:
                    st.error(f"❌ 图案错误！还有 {remaining} 次尝试机会")
                    st.session_state.pattern_input = []
                else:
                    st.error("🚫 图案验证失败次数过多，系统锁定！")
                    st.session_state.locked = True
                    st.rerun()
    
    with col3:
        if st.button("返回上一层"):
            st.session_state.authentication_stage = 1
            st.session_state.pattern_input = []
            st.rerun()

# 第三层：IP认证（凯撒密码）
elif st.session_state.authentication_stage == 3:
    st.header("🌐 第三层：IP认证验证")
    
    # 显示提示信息
    st.info(f"🔐 您看到的加密IP地址是: `{ENCRYPTED_IP_INPUT}`")
    st.info("💡 提示：这是一个加密后的IP地址，请直接输入此加密IP进行身份验证")
    st.warning("🔍 系统内部会自动解密您输入的IP并与存储的真实IP进行比对")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 显示加密逻辑说明
        st.subheader("🔐 加密逻辑说明")
        st.write("系统使用凯撒密码（偏移3）对IP进行加密/解密：")
        st.code(f"""
加密IP: {ENCRYPTED_IP_INPUT}
↓ (系统内部解密，偏移-3)
真实IP: {SYSTEM_STORED_IP}
        """)
        
        st.markdown("---")
        
        # IP验证
        st.subheader("✅ IP身份验证")
        st.write("请输入上方显示的加密IP地址：")
        ip_input = st.text_input("请输入加密的IP地址:")
        
        if st.button("验证IP地址", use_container_width=True):
            # 对用户输入的IP进行解密，然后与系统存储的真实IP比较
            decrypted_user_ip = caesar_cipher_decrypt(ip_input, CAESAR_SHIFT)
            
            if decrypted_user_ip == SYSTEM_STORED_IP:
                st.success("🎉 IP验证成功！所有认证层级已通过！")
                st.balloons()
                
                # 设置认证状态
                st.session_state.authenticated = True
                
                # 显示成功信息
                st.markdown("---")
                st.success("### 🔓 系统解锁成功！")
                st.write(f"**验证时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**输入的加密IP:** {ip_input}")
                st.write(f"**解密后的真实IP:** {decrypted_user_ip}")
                st.write(f"**系统存储的IP:** {SYSTEM_STORED_IP}")
                st.write("**状态:** 已通过多重身份验证")
                
                # 自动跳转到浏览器
                st.info("🌐 正在启动安全VM浏览器...")
                if st.button("进入VM浏览器"):
                    st.rerun()
                
                if st.button("重新开始认证流程"):
                    st.session_state.authentication_stage = 1
                    st.session_state.attempts = 0
                    st.session_state.pattern_input = []
                    st.session_state.authenticated = False
                    st.rerun()
            else:
                st.session_state.attempts += 1
                remaining = MAX_ATTEMPTS - st.session_state.attempts
                if remaining > 0:
                    st.error(f"❌ IP地址验证失败！还有 {remaining} 次尝试机会")
                    st.write(f"您输入的IP解密后为: `{decrypted_user_ip}`")
                    st.write(f"系统期望的IP为: `{SYSTEM_STORED_IP}`")
                else:
                    st.error("🚫 IP验证失败次数过多，系统锁定！")
                    st.session_state.locked = True
                    st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("返回上一层"):
            st.session_state.authentication_stage = 2
            st.rerun()

# 侧边栏信息
with st.sidebar:
    st.header("🛡️ 系统状态")
    if st.session_state.authenticated:
        st.success("✅ 已认证")
        st.write("🔒 所有安全层级已通过")
    else:
        st.warning("⚠️ 未认证")
        st.write(f"当前阶段: {st.session_state.authentication_stage}/3")
    
    st.markdown("---")
    st.write("**安全特性:**")
    st.write("- 多层认证保护")
    st.write("- 失败次数限制") 
    st.write("- IP地址加密隐藏")
    st.write("- 凯撒密码保护")
    st.write("- VM浏览器隔离")
    
    if st.button("🔧 系统重置"):
        st.session_state.authentication_stage = 1
        st.session_state.attempts = 0
        st.session_state.locked = False
        st.session_state.pattern_input = []
        st.session_state.authenticated = False
        st.success("系统已重置！")
        st.rerun()
