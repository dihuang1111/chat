import streamlit as st
import hashlib
import base64
import secrets
import re
from cryptography.fernet import Fernet
import os

# Generate a key for encryption (in production, store this securely)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Caesar cipher shift (explicitly set to 3)
CAESAR_SHIFT = 3

# Function to encrypt IP using Caesar cipher (applied to each octet)
def encrypt_ip(ip):
    def shift_octet(octet_str):
        if '.' in octet_str:
            nums = octet_str.split('.')
            shifted = '.'.join(str((int(n) + CAESAR_SHIFT) % 10) for n in nums)
            return shifted
        return octet_str
    return shift_octet(ip)

# Function to decrypt IP using Caesar cipher
def decrypt_ip(encrypted_ip):
    def unshift_octet(octet_str):
        if '.' in octet_str:
            nums = octet_str.split('.')
            unshifted = '.'.join(str((int(n) - CAESAR_SHIFT) % 10) for n in nums)
            return unshifted
        return octet_str
    return unshift_octet(encrypted_ip)

# Simulated user database updated without face_data
USER_DB = {
    "myuser": {
        "pincode": "abcdef",
        "pattern": "1-2-5-8-9-34",
        "allowed_ip": encrypt_ip("192.168.1.100")  # Encrypted with shift of 3
    }
}

# Streamlit app
def main():
    st.set_page_config(page_title="MFA with Streamlit", page_icon="🔒")
    st.title("Multi-Factor Authentication")

    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = secrets.token_hex(16)
        st.session_state.step = "ip_verify"  # Start with IP verification
        st.session_state.status = None
        st.session_state.message = ""

    # Function to verify IP
    def verify_ip(user_ip, user_id="myuser"):
        decrypted_allowed_ip = decrypt_ip(USER_DB[user_id]["allowed_ip"])
        if user_ip == decrypted_allowed_ip:
            st.session_state.step = "pincode"
            st.session_state.status = "success"
            st.session_state.message = "IP verified"
        else:
            st.session_state.status = "failure"
            st.session_state.message = "Invalid IP address"

    # Function to verify PIN
    def verify_pin(pincode, user_id="myuser"):
        if user_id in USER_DB and pincode == USER_DB[user_id]["pincode"]:
            st.session_state.step = "pattern"
            st.session_state.status = "success"
            st.session_state.message = "PIN verified"
        else:
            st.session_state.status = "failure"
            st.session_state.message = "Invalid PIN"

    # Function to verify pattern
    def verify_pattern(pattern, user_id="myuser"):
        if st.session_state.step == "pattern":
            if pattern == USER_DB[user_id]["pattern"]:
                st.session_state.step = "vm_preview"  # Move to VM preview after pattern verification
                st.session_state.status = "success"
                st.session_state.message = "Pattern verified"
            else:
                st.session_state.status = "failure"
                st.session_state.message = "Invalid pattern"
        else:
            st.session_state.status = "failure"
            st.session_state.message = "Step mismatch"

    # Step 0: IP Verification
    if st.session_state.step == "ip_verify":
        st.subheader("Step 0: Enter Your IP Address")
        st.write("Enter your IP address to proceed (e.g., 192.168.1.100)")
        with st.form("ip_form"):
            user_ip = st.text_input("IP Address")
            submitted = st.form_submit_button("Verify IP")
            if submitted:
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", user_ip):
                    verify_ip(user_ip)
                else:
                    st.session_state.status = "failure"
                    st.session_state.message = "Invalid IP format"

    # Step 1: PIN Code Verification
    elif st.session_state.step == "pincode":
        st.subheader("Step 1: Enter PIN Code")
        with st.form("pin_form"):
            pincode = st.text_input("PIN Code", type="password")
            submitted = st.form_submit_button("Verify PIN")
            if submitted:
                if pincode:
                    verify_pin(pincode)
                else:
                    st.session_state.status = "failure"
                    st.session_state.message = "Please enter a PIN code"

    # Step 2: Pattern Password
    elif st.session_state.step == "pattern":
        st.subheader("Step 2: Enter Pattern Password")
        st.write("Enter pattern as numbers (e.g., 1-2-5-8-9-34 for a 3x3 grid)")
        with st.form("pattern_form"):
            pattern = st.text_input("Pattern")
            submitted = st.form_submit_button("Verify Pattern")
            if submitted:
                if pattern and re.match(r"^\d+(-\d+)*$", pattern):
                    verify_pattern(pattern)
                else:
                    st.session_state.status = "failure"
                    st.session_state.message = "Invalid pattern format. Use numbers separated by hyphens (e.g., 1-2-5-8-9-34)"

    # Step 3: VM Browser Preview
    elif st.session_state.step == "vm_preview":
        st.subheader("Step 3: VM Browser Preview")
        st.write("MFA completed! Below is a simulated VM browser preview. For a real VM, use a service like Skytap or Azure Bastion with your credentials.")
        st.image("https://via.placeholder.com/800x600.png?text=VM+Browser+Preview", caption="Simulated VM Browser Screen")
        st.write("Note: This is a placeholder. Integrate with a VM service API for real-time preview.")

    # Display status message
    if st.session_state.message:
        if st.session_state.status == "success":
            st.success(st.session_state.message)
        else:
            st.error(st.session_state.message)

if __name__ == "__main__":
    main()
