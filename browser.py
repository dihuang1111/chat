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
    """创建VM浏览器界面"""
    st.markdown("""
    <style>
    .browser-container {
        border: 2px solid #333;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 10px;
        margin: 10px 0;
    }
    .browser-header {
        background: #2c3e50;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .browser-controls {
        display: flex;
        gap: 5px;
    }
    .control-btn {
        width: 15px;
        height: 15px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
    }
    .close-btn { background: #ff5f56; }
    .minimize-btn { background: #ffbd2e; }
    .maximize-btn { background: #27ca3f; }
    .browser-viewport {
        background: white;
        border-radius: 5px;
        min-height: 600px;
        padding: 20px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
    }
    .url-bar {
        background: #34495e;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 15px;
        width: 70%;
        margin: 0 10px;
    }
    .nav-btn {
        background: #3498db;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        cursor: pointer;
        margin: 0 2px;
    }
    .nav-btn:hover {
        background: #2980b9;
    }
    .status-bar {
        background: #ecf0f1;
        padding: 5px 15px;
        border-radius: 0 0 5px 5px;
        font-size: 12px;
        color: #7f8c8d;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="browser-container">', unsafe_allow_html=True)
    
    # 浏览器标题栏
    st.markdown("""
    <div class="browser-header">
        <div class="browser-controls">
            <div class="control-btn close-btn"></div>
            <div class="control-btn minimize-btn"></div>
            <div class="control-btn maximize-btn"></div>
        </div>
        <span style="color: white; font-weight: bold;">🔐 Secure VM Browser</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 导航栏
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 6, 1, 1])
    
    with col1:
        if st.button("⬅️", help="后退"):
            if st.session_state.browser_history:
                st.session_state.current_url = st.session_state.browser_history.pop()
                st.rerun()
    
    with col2:
        if st.button("➡️", help="前进"):
            pass  # 前进功能可以根据需要实现
    
    with col3:
        if st.button("🔄", help="刷新"):
            st.rerun()
    
    with col4:
        new_url = st.text_input("", 
                                value=st.session_state.current_url, 
                                placeholder="输入网址...",
                                key="url_input")
    
    with col5:
        if st.button("🏠", help="主页"):
            st.session_state.browser_history.append(st.session_state.current_url)
            st.session_state.current_url = "https://www.google.com"
            st.rerun()
    
    with col6:
        if st.button("Go"):
            if new_url != st.session_state.current_url:
                st.session_state.browser_history.append(st.session_state.current_url)
                st.session_state.current_url = new_url
                st.rerun()
    
    # 浏览器视口
    st.markdown('<div class="browser-viewport">', unsafe_allow_html=True)
    
    # 模拟网页内容显示
    if st.session_state.current_url:
        st.markdown(f"### 🌐 正在浏览: {st.session_state.current_url}")
        
        # 根据URL显示不同内容
        if "google.com" in st.session_state.current_url.lower():
            display_google_page()
        elif "youtube.com" in st.session_state.current_url.lower():
            display_youtube_page()
        elif "github.com" in st.session_state.current_url.lower():
            display_github_page()
        else:
            display_generic_page()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 状态栏
    st.markdown(f"""
    <div class="status-bar">
        📡 连接状态: 安全连接 | 🔒 SSL证书: 有效 | ⏰ 加载时间: 0.5s | 📍 当前: {st.session_state.current_url}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_google_page():
    """显示Google页面模拟"""
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1 style="color: #4285f4; font-size: 80px; margin: 0;">Google</h1>
        <div style="margin: 30px 0;">
            <input type="text" placeholder="搜索 Google 或输入网址" 
                   style="width: 400px; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none;">
        </div>
        <div>
            <button style="background: #f8f9fa; border: 1px solid #f8f9fa; border-radius: 4px; padding: 10px 20px; margin: 0 5px;">Google 搜索</button>
            <button style="background: #f8f9fa; border: 1px solid #f8f9fa; border-radius: 4px; padding: 10px 20px; margin: 0 5px;">手气不错</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_youtube_page():
    """显示YouTube页面模拟"""
    st.markdown("""
    <div style="background: #0f0f0f; color: white; padding: 20px; border-radius: 10px;">
        <h2 style="color: #ff0000;">📺 YouTube</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            <div style="background: #1a1a1a; padding: 15px; border-radius: 8px;">
                <div style="background: #333; height: 150px; border-radius: 5px; display: flex; align-items: center; justify-content: center;">
                    📹 视频缩略图
                </div>
                <h4>示例视频标题 1</h4>
                <p style="color: #aaa;">频道名称 • 100万次观看 • 1天前</p>
            </div>
            <div style="background: #1a1a1a; padding: 15px; border-radius: 8px;">
                <div style="background: #333; height: 150px; border-radius: 5px; display: flex; align-items: center; justify-content: center;">
                    📹 视频缩略图
                </div>
                <h4>示例视频标题 2</h4>
                <p style="color: #aaa;">频道名称 • 500万次观看 • 3天前</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_github_page():
    """显示GitHub页面模拟"""
    st.markdown("""
    <div style="background: #0d1117; color: white; padding: 20px; border-radius: 10px;">
        <h2 style="color: white;">🐙 GitHub</h2>
        <div style="background: #161b22; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>📁 示例代码仓库</h3>
            <div style="display: flex; gap: 20px; margin: 15px 0;">
                <span style="background: #238636; padding: 5px 10px; border-radius: 15px; font-size: 12px;">Python</span>
                <span style="color: #f85149;">⭐ 1.2k</span>
                <span style="color: #7d8590;">🍴 234</span>
            </div>
            <p style="color: #e6edf3;">这是一个示例代码仓库的描述信息...</p>
            <div style="margin-top: 15px;">
                <button style="background: #238636; color: white; border: none; padding: 8px 16px; border-radius: 6px; margin-right: 10px;">📥 Code</button>
                <button style="background: #21262d; color: white; border: 1px solid #30363d; padding: 8px 16px; border-radius: 6px;">⭐ Star</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_generic_page():
    """显示通用页面"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #74b9ff, #0984e3); color: white; padding: 30px; border-radius: 10px; text-align: center;">
        <h2>🌐 网页内容模拟</h2>
        <p>当前正在访问: <strong>{st.session_state.current_url}</strong></p>
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>页面内容</h3>
            <p>这里显示网页的模拟内容。在实际的VM浏览器中，这里会显示真实的网页内容。</p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 20px;">
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 5px; width: 150px;">
                    <h4>功能模块 1</h4>
                    <p>模拟内容</p>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 5px; width: 150px;">
                    <h4>功能模块 2</h4>
                    <p>模拟内容</p>
                </div>
            </div>
        </div>
        <p style="font-size: 14px; opacity: 0.8;">💡 提示: 这是一个安全的VM浏览环境，所有网络活动都经过加密和隔离处理。</p>
    </div>
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

# 配置信息
CORRECT_PIN = "11912"  # 第一层PIN码
CORRECT_PATTERN = [1, 6, 6, 4, 5]  # 第二层正确图案 (示例：1-2-3-4-5)
ENCRYPTED_IP_INPUT = "421.499.553.03"  # 用户看到的加密IP
CAESAR_SHIFT = 3  # 凯撒密码偏移量
SYSTEM_STORED_IP = caesar_cipher_decrypt(ENCRYPTED_IP_INPUT, CAESAR_SHIFT)  # 系统存储的解密后真实IP
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
    st.header("🛡️ 安全信息")
    st.write("**系统配置:**")
    st.write(f"- PIN码: {'*' * len(CORRECT_PIN)}")
    st.write(f"- 图案: {' → '.join(map(str, CORRECT_PATTERN))}")
    st.write(f"- 显示的加密IP: {ENCRYPTED_IP_INPUT}")
    st.write(f"- 系统存储的真实IP: {SYSTEM_STORED_IP}")
    st.write(f"- 解密偏移量: {CAESAR_SHIFT}")
    
    st.markdown("---")
    st.write("**安全特性:**")
    st.write("- 多层认证保护")
    st.write("- 失败次数限制")
    st.write("- IP地址加密隐藏")
    st.write("- 凯撒密码保护")
    
    if st.button("🔧 管理员重置"):
        st.session_state.authentication_stage = 1
        st.session_state.attempts = 0
        st.session_state.locked = False
        st.session_state.pattern_input = []
        st.session_state.authenticated = False
        st.success("系统已重置！")
        st.rerun()
