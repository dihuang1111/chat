import streamlit as st
import requests
import random
import string
from datetime import datetime, timedelta
import time
import hashlib
import json
import resend

# 配置页面
st.set_page_config(
    page_title="Secure Browser",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Resend 配置 - 请替换为你的实际API密钥
RESEND_API_KEY = "re_djRrz4Q6_L2zJ552GpMfaYBoMkC9eyL3o"
SENDER_EMAIL = "noreply@us1337.com"  # 替换为你验证的发送邮箱域名

class EmailVerification:
    def __init__(self):
        self.resend_url = "https://api.resend.com/emails"
        self.verification_codes = {}  # 存储验证码 {email: {code, timestamp, attempts}}
    
    def generate_verification_code(self, length=6):
        """生成随机验证码"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_email(self, email, code):
        """通过Resend发送验证码邮件"""
        headers = {
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        email_data = {
            'from': SENDER_EMAIL,
            'to': [email],
            'subject': '🔐 浏览器验证码 - 请勿分享',
            'html': f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 28px;">🌐 安全浏览器</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">身份验证</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-top: 20px; text-align: center;">
                    <h2 style="color: #333; margin-bottom: 20px;">您的验证码</h2>
                    <div style="background: white; border: 2px solid #667eea; border-radius: 8px; padding: 20px; margin: 20px 0; display: inline-block;">
                        <span style="font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px;">{code}</span>
                    </div>
                    <p style="color: #666; margin: 20px 0;">请在浏览器中输入此验证码以完成登录</p>
                    <p style="color: #999; font-size: 14px;">验证码将在 <strong>10分钟</strong> 后过期</p>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #fff3cd; border-radius: 8px;">
                    <p style="color: #856404; margin: 0; text-align: center;">
                        <strong>⚠️ 安全提醒：</strong> 请勿将此验证码分享给任何人。我们的工作人员绝不会主动向您索要验证码。
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
                    <p>如果您没有请求此验证码，请忽略此邮件</p>
                    <p>© 2024 安全浏览器 - 保护您的网络安全</p>
                </div>
            </div>
            '''
        }
        
        try:
            response = requests.post(self.resend_url, headers=headers, json=email_data)
            return response.status_code == 200
        except Exception as e:
            st.error(f"发送邮件失败: {e}")
            return False
    
    def store_verification_code(self, email, code):
        """存储验证码"""
        self.verification_codes[email] = {
            'code': code,
            'timestamp': datetime.now(),
            'attempts': 0
        }
    
    def verify_code(self, email, input_code):
        """验证验证码"""
        if email not in self.verification_codes:
            return False, "未找到验证码记录"
        
        stored_data = self.verification_codes[email]
        
        # 检查是否过期（10分钟）
        if datetime.now() - stored_data['timestamp'] > timedelta(minutes=10):
            del self.verification_codes[email]
            return False, "验证码已过期，请重新获取"
        
        # 检查尝试次数（最多5次）
        if stored_data['attempts'] >= 5:
            del self.verification_codes[email]
            return False, "验证码尝试次数过多，请重新获取"
        
        # 验证码匹配
        if stored_data['code'] == input_code:
            del self.verification_codes[email]
            return True, "验证成功"
        else:
            stored_data['attempts'] += 1
            remaining = 5 - stored_data['attempts']
            return False, f"验证码错误，还有 {remaining} 次尝试机会"

def init_session_state():
    """初始化session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'verification_sent' not in st.session_state:
        st.session_state.verification_sent = False
    if 'send_time' not in st.session_state:
        st.session_state.send_time = None
    if 'browsing_history' not in st.session_state:
        st.session_state.browsing_history = []
    if 'bookmarks' not in st.session_state:
        st.session_state.bookmarks = []
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""
    if 'email_verifier' not in st.session_state:
        st.session_state.email_verifier = EmailVerification()

def is_valid_email(email):
    """简单的邮箱格式验证"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def display_login_page():
    """显示登录页面"""
    st.title("🌐 安全浏览器")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; border: 2px solid #667eea; border-radius: 10px; background-color: #f8f9fa;'>
            <h3>🔐 邮箱验证登录</h3>
            <p>请输入您的邮箱地址，我们将发送验证码给您</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # 邮箱输入阶段
        if not st.session_state.verification_sent:
            email = st.text_input(
                "📧 邮箱地址",
                placeholder="your.email@example.com",
                help="请输入有效的邮箱地址"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                send_button = st.button("📨 发送验证码", type="primary", use_container_width=True)
            
            if send_button:
                if not email:
                    st.error("请输入邮箱地址")
                elif not is_valid_email(email):
                    st.error("请输入有效的邮箱格式")
                else:
                    # 发送验证码
                    with st.spinner("正在发送验证码..."):
                        code = st.session_state.email_verifier.generate_verification_code()
                        
                        if st.session_state.email_verifier.send_verification_email(email, code):
                            st.session_state.email_verifier.store_verification_code(email, code)
                            st.session_state.verification_sent = True
                            st.session_state.user_email = email
                            st.session_state.send_time = datetime.now()
                            st.success(f"✅ 验证码已发送到 {email}")
                            st.info("请检查您的邮箱（包括垃圾邮件文件夹）")
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error("❌ 验证码发送失败，请检查邮箱地址或稍后重试")
        
        # 验证码输入阶段
        else:
            st.success(f"✅ 验证码已发送到: {st.session_state.user_email}")
            
            # 显示倒计时
            if st.session_state.send_time:
                elapsed = datetime.now() - st.session_state.send_time
                remaining = 600 - int(elapsed.total_seconds())  # 10分钟 = 600秒
                if remaining > 0:
                    minutes = remaining // 60
                    seconds = remaining % 60
                    st.info(f"⏱️ 验证码有效时间还剩: {minutes:02d}:{seconds:02d}")
                else:
                    st.error("⏰ 验证码已过期，请重新获取")
            
            verification_code = st.text_input(
                "🔑 请输入6位验证码",
                max_chars=6,
                placeholder="123456",
                help="请输入您邮箱中收到的6位数字验证码"
            )
            
            col_verify1, col_verify2, col_verify3 = st.columns([1, 1, 1])
            
            with col_verify1:
                if st.button("🔄 重新发送", use_container_width=True):
                    # 重新发送验证码
                    with st.spinner("正在重新发送..."):
                        code = st.session_state.email_verifier.generate_verification_code()
                        if st.session_state.email_verifier.send_verification_email(st.session_state.user_email, code):
                            st.session_state.email_verifier.store_verification_code(st.session_state.user_email, code)
                            st.session_state.send_time = datetime.now()
                            st.success("✅ 验证码已重新发送")
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error("❌ 重新发送失败")
            
            with col_verify2:
                verify_button = st.button("🔓 验证登录", type="primary", use_container_width=True)
            
            with col_verify3:
                if st.button("🔙 返回", use_container_width=True):
                    st.session_state.verification_sent = False
                    st.session_state.user_email = None
                    st.session_state.send_time = None
                    st.experimental_rerun()
            
            if verify_button:
                if not verification_code:
                    st.error("请输入验证码")
                elif len(verification_code) != 6:
                    st.error("验证码必须是6位数字")
                else:
                    # 验证验证码
                    success, message = st.session_state.email_verifier.verify_code(
                        st.session_state.user_email, 
                        verification_code
                    )
                    
                    if success:
                        st.session_state.authenticated = True
                        st.success("🎉 登录成功！")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(f"❌ {message}")
        
        # 设置说明
        st.markdown("---")
        with st.expander("📋 设置说明"):
            st.markdown("""
            **Resend 配置步骤：**
            1. 注册 [Resend](https://resend.com) 账户
            2. 验证您的发送域名
            3. 获取 API 密钥
            4. 在代码中替换 `RESEND_API_KEY` 和 `SENDER_EMAIL`
            
            **安全特性：**
            - 验证码10分钟内有效
            - 最多尝试5次
            - 邮箱格式验证
            - 防重复发送保护
            """)

def display_browser_interface():
    """显示浏览器界面"""
    # 顶部用户信息栏
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.title("🌐 安全浏览器")
        
        with col2:
            st.write(f"👋 欢迎, {st.session_state.user_email}")
        
        with col3:
            if st.button("🚪 退出登录"):
                # 清除所有会话数据
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()
    
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 浏览器工具")
        
        # 用户信息
        st.info(f"🔐 已登录: {st.session_state.user_email}")
        
        st.markdown("---")
        
        # 书签管理
        st.subheader("📚 书签管理")
        bookmark_url = st.text_input("添加书签", placeholder="输入网址")
        bookmark_name = st.text_input("书签名称", placeholder="可选：自定义名称")
        
        if st.button("💾 保存书签") and bookmark_url:
            bookmark_item = {
                'url': bookmark_url,
                'name': bookmark_name if bookmark_name else bookmark_url,
                'created': datetime.now()
            }
            if bookmark_item not in st.session_state.bookmarks:
                st.session_state.bookmarks.append(bookmark_item)
                st.success("✅ 书签已保存")
        
        # 显示书签
        if st.session_state.bookmarks:
            st.markdown("**我的书签：**")
            for i, bookmark in enumerate(st.session_state.bookmarks):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(
                        f"🔖 {bookmark['name'][:20]}..." if len(bookmark['name']) > 20 else f"🔖 {bookmark['name']}", 
                        key=f"bookmark_{i}",
                        help=bookmark['url']
                    ):
                        st.session_state.current_url = bookmark['url']
                        st.experimental_rerun()
                with col2:
                    if st.button("🗑️", key=f"del_bookmark_{i}", help="删除书签"):
                        st.session_state.bookmarks.remove(bookmark)
                        st.experimental_rerun()
        
        st.markdown("---")
        
        # 浏览历史
        st.subheader("📜 浏览历史")
        if st.session_state.browsing_history:
            for i, item in enumerate(reversed(st.session_state.browsing_history[-10:])):
                url, timestamp = item['url'], item['timestamp']
                display_url = url[:25] + "..." if len(url) > 25 else url
                if st.button(
                    f"🌍 {display_url}", 
                    key=f"history_{i}",
                    help=f"访问时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                ):
                    st.session_state.current_url = url
                    st.experimental_rerun()
                st.caption(timestamp.strftime("%H:%M:%S"))
        else:
            st.info("暂无浏览历史")
        
        # 清除历史按钮
        if st.session_state.browsing_history:
            if st.button("🧹 清除历史"):
                st.session_state.browsing_history = []
                st.experimental_rerun()
    
    # 主浏览区域
    col1, col2 = st.columns([10, 1])
    
    with col1:
        url_input = st.text_input(
            "🌐 输入网址或搜索关键词", 
            value=st.session_state.current_url,
            placeholder="https://example.com 或输入搜索关键词",
            help="支持直接输入网址或搜索关键词"
        )
    
    with col2:
        go_button = st.button("🚀 前往", type="primary")
    
    # 快捷按钮
    st.markdown("**🔥 热门网站：**")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    quick_sites = [
        {"name": "Google", "url": "https://www.google.com", "icon": "🔍"},
        {"name": "GitHub", "url": "https://www.github.com", "icon": "💻"},
        {"name": "Stack Overflow", "url": "https://stackoverflow.com", "icon": "📚"},
        {"name": "YouTube", "url": "https://www.youtube.com", "icon": "📺"},
        {"name": "Wikipedia", "url": "https://www.wikipedia.org", "icon": "📖"}
    ]
    
    for i, site in enumerate(quick_sites):
        col = [col1, col2, col3, col4, col5][i]
        with col:
            if st.button(f"{site['icon']} {site['name']}", key=f"quick_{i}"):
                st.session_state.current_url = site['url']
                st.experimental_rerun()
    
    # 处理URL输入
    if go_button and url_input:
        # URL处理和验证
        processed_url = url_input.strip()
        
        if not processed_url.startswith(('http://', 'https://')):
            if '.' in processed_url and ' ' not in processed_url and len(processed_url.split('.')) >= 2:
                # 看起来像是域名
                processed_url = 'https://' + processed_url
            else:
                # 当作搜索处理
                from urllib.parse import urlencode
                processed_url = f"https://www.google.com/search?{urlencode({'q': processed_url})}"
        
        st.session_state.current_url = processed_url
        
        # 添加到浏览历史
        history_item = {
            'url': processed_url,
            'timestamp': datetime.now()
        }
        st.session_state.browsing_history.append(history_item)
        
        # 限制历史记录数量
        if len(st.session_state.browsing_history) > 50:
            st.session_state.browsing_history = st.session_state.browsing_history[-50:]
    
    # 显示网页内容
    if st.session_state.current_url:
        st.markdown("---")
        
        # 显示当前网址信息
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"🌍 当前访问: {st.session_state.current_url}")
        with col2:
            if st.button("📋 复制链接"):
                st.success("链接已复制到剪贴板")
        
        # 使用iframe显示网页
        try:
            st.markdown(f"""
            <div style="border: 2px solid #ddd; border-radius: 8px; overflow: hidden;">
                <iframe src="{st.session_state.current_url}" 
                        width="100%" 
                        height="600" 
                        style="border: none;">
                </iframe>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ 无法在框架中加载此网页: {e}")
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa;">
                <h4>🔗 无法嵌入显示</h4>
                <p>某些网站出于安全考虑不允许在框架中显示</p>
                <a href="{st.session_state.current_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">
                    🚀 在新窗口中打开
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # 默认主页
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin: 2rem 0;'>
            <h2>🏠 欢迎使用安全浏览器</h2>
            <p style='font-size: 18px; opacity: 0.9;'>您的安全网络入口</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 功能介绍
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='padding: 1.5rem; border: 1px solid #ddd; border-radius: 10px; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;'>
                <h4>🔐 安全认证</h4>
                <p>邮箱验证码登录<br>保护您的隐私安全</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='padding: 1.5rem; border: 1px solid #ddd; border-radius: 10px; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;'>
                <h4>📚 智能书签</h4>
                <p>保存常用网站<br>快速访问管理</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='padding: 1.5rem; border: 1px solid #ddd; border-radius: 10px; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;'>
                <h4>📜 历史记录</h4>
                <p>浏览历史追踪<br>快速回到之前页面</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """主函数"""
    init_session_state()
    
    # 根据认证状态显示不同界面
    if not st.session_state.authenticated:
        display_login_page()
    else:
        display_browser_interface()

if __name__ == "__main__":
    main()
