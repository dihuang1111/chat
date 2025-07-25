import streamlit as st
import asyncio
import json
import hashlib
import base64
import secrets
import re
from datetime import datetime, timedelta

# Simulated user database (replace with real database in production)
USER_DB = {
    "user1": {
        "pincode": "133788",
        "pattern": "1-5-5-6-9",  # Example pattern (grid positions)
        "face_data": "encoded_face_data"  # Placeholder for face recognition data
    }
}

# WebSocket server state
sessions = {}

async def mfa_server(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            session_id = data.get("session_id")
            step = data.get("step")
            user_id = data.get("user_id", "user1")  # Default for demo
            payload = data.get("payload")

            response = {"session_id": session_id, "step": step, "status": "failure", "message": ""}

            if step == "pincode":
                if user_id in USER_DB and payload == USER_DB[user_id]["pincode"]:
                    response["status"] = "success"
                    response["message"] = "PIN verified"
                    sessions[session_id] = {"user_id": user_id, "step": "pattern"}
                else:
                    response["message"] = "Invalid PIN"
            
            elif step == "pattern":
                if session_id in sessions and sessions[session_id]["step"] == "pattern":
                    if payload == USER_DB[user_id]["pattern"]:
                        response["status"] = "success"
                        response["message"] = "Pattern verified"
                        sessions[session_id]["step"] = "face"
                    else:
                        response["message"] = "Invalid pattern"
                else:
                    response["message"] = "Session invalid or step mismatch"
            
            elif step == "face":
                if session_id in sessions and sessions[session_id]["step"] == "face":
                    # Placeholder for face verification
                    # In a real app, compare payload (e.g., encoded face image) with stored face data
                    # Example: use face_recognition library or external API
                    if payload == "simulated_face_data":  # Replace with actual face verification
                        response["status"] = "success"
                        response["message"] = "Face verified"
                        sessions[session_id]["step"] = "complete"
                    else:
                        response["message"] = "Face verification failed"
                else:
                    response["message"] = "Session invalid or step mismatch"
            
            await websocket.send(json.dumps(response))
    except Exception as e:
        await websocket.send(json.dumps({"status": "error", "message": str(e)}))

# Start WebSocket server in the background
async def start_ws_server():
    server = await websockets.serve(mfa_server, "localhost", 8765)
    await server.wait_closed()

# Run WebSocket server in a separate thread
def run_ws_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_ws_server())

# Streamlit app
def main():
    st.set_page_config(page_title="MFA with WebSocket", page_icon="🔒")
    st.title("Multi-Factor Authentication")

    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = secrets.token_hex(16)
        st.session_state.step = "pincode"
        st.session_state.status = None
        st.session_state.message = ""

    # JavaScript for WebSocket client
    st.markdown("""
    <script>
        let ws = null;
        function connectWebSocket(sessionId, step, payload) {
            ws = new WebSocket("ws://localhost:8765");
            ws.onopen = function() {
                ws.send(JSON.stringify({
                    session_id: sessionId,
                    step: step,
                    user_id: "user1", // Replace with dynamic user input
                    payload: payload
                }));
            };
            ws.onmessage = function(event) {
                const response = JSON.parse(event.data);
                // Update Streamlit session state via hidden input
                document.getElementById("ws_response").value = JSON.stringify(response);
                document.getElementById("ws_form").submit();
            };
            ws.onerror = function(error) {
                console.error("WebSocket error:", error);
            };
        }
    </script>
    <form id="ws_form" action="" method="post">
        <input type="hidden" id="ws_response" name="ws_response">
    </form>
    """, unsafe_allow_html=True)

    # Handle WebSocket response
    ws_response = st.experimental_get_query_params().get("ws_response", [None])[0]
    if ws_response:
        response = json.loads(ws_response)
        st.session_state.status = response["status"]
        st.session_state.message = response["message"]
        if response["status"] == "success":
            st.session_state.step = sessions.get(st.session_state.session_id, {}).get("step", st.session_state.step)

    # Step 1: PIN Code Verification
    if st.session_state.step == "pincode":
        st.subheader("Step 1: Enter PIN Code")
        pincode = st.text_input("PIN Code", type="password")
        if st.button("Verify PIN"):
            if pincode:
                st.markdown(f"""
                <script>
                    connectWebSocket("{st.session_state.session_id}", "pincode", "{pincode}");
                </script>
                """, unsafe_allow_html=True)
            else:
                st.error("Please enter a PIN code")

    # Step 2: Pattern Password
    elif st.session_state.step == "pattern":
        st.subheader("Step 2: Enter Pattern Password")
        st.write("Enter pattern as numbers (e.g., 1-2-5-8-9 for a 3x3 grid)")
        pattern = st.text_input("Pattern")
        if st.button("Verify Pattern"):
            if pattern and re.match(r"^\d+(-\d+)*$", pattern):
                st.markdown(f"""
                <script>
                    connectWebSocket("{st.session_state.session_id}", "pattern", "{pattern}");
                </script>
                """, unsafe_allow_html=True)
            else:
                st.error("Invalid pattern format. Use numbers separated by hyphens (e.g., 1-2-5-8-9)")

    # Step 3: Face Verification (Placeholder)
    elif st.session_state.step == "face":
        st.subheader("Step 3: Face Verification")
        st.write("This is a placeholder for face verification. Upload an image or use camera input.")
        uploaded_file = st.file_uploader("Upload face image (placeholder)", type=["jpg", "png"])
        if st.button("Verify Face"):
            if uploaded_file:
                # Simulate face data encoding (replace with actual face recognition)
                face_data = base64.b64encode(uploaded_file.read()).decode()
                st.markdown(f"""
                <script>
                    connectWebSocket("{st.session_state.session_id}", "face", "simulated_face_data");
                </script>
                """, unsafe_allow_html=True)
            else:
                st.error("Please upload an image")

    # Completion
    elif st.session_state.step == "complete":
        st.success("MFA Completed Successfully!")
        st.balloons()

    # Display status message
    if st.session_state.message:
        if st.session_state.status == "success":
            st.success(st.session_state.message)
        else:
            st.error(st.session_state.message)

if __name__ == "__main__":
    import threading
    ws_thread = threading.Thread(target=run_ws_server, daemon=True)
    ws_thread.start()
    main()
