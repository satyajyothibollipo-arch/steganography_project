import streamlit as st
from PIL import Image
import numpy as np
from gtts import gTTS
import io

st.set_page_config(page_title="Steganography Voice App")

st.title("🔐 Image Steganography with Voice")

# -----------------------------
# Language Selection
# -----------------------------
lang_option = st.selectbox(
    "Select Voice Language",
    ["English", "Telugu", "Hindi"]
)

lang_map = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi"
}

# -----------------------------
# Upload Image
# -----------------------------
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

message = st.text_input("Enter message")

# -----------------------------
# Functions
# -----------------------------

def encode_message(img, msg):
    msg += "###"   # delimiter
    binary_msg = ''.join([format(ord(i), '08b') for i in msg])

    data = np.array(img)
    flat = data.flatten()

    for i in range(len(binary_msg)):
       flat[i] = (flat[i] & 254) | int(binary_msg[i])

    encoded = flat.reshape(data.shape)
    return Image.fromarray(encoded.astype('uint8'))


def decode_message(img):
    data = np.array(img)
    flat = data.flatten()

    bits = [str(flat[i] & 1) for i in range(len(flat))]
    chars = []

    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        char = chr(int(''.join(byte), 2))
        chars.append(char)
        if ''.join(chars).endswith("###"):
            break

    return ''.join(chars).replace("###", "")


# -----------------------------
# Show Image
# -----------------------------
if uploaded_file:
    image = Image.open(uploaded_file).convert('L')
    st.image(image, caption="Input Image", use_column_width=True)

    # -------------------------
    # Hide Button
    # -------------------------
    if st.button("🔒 Hide Message"):
        if message:
            encoded_img = encode_message(image, message)
            st.session_state["encoded_img"] = encoded_img

            st.success("Message Hidden Successfully!")
            st.image(encoded_img, caption="Encoded Image", use_column_width=True)

        else:
            st.error("Enter message first!")

    # -------------------------
    # Retrieve Button
    # -------------------------
    if st.button("🔓 Retrieve Message"):

        if "encoded_img" in st.session_state:

            decoded_msg = decode_message(st.session_state["encoded_img"])

            st.success("Message Retrieved Successfully!")
            st.write("### Hidden Message:")
            st.write(decoded_msg)

            # ---------------------
            # TEXT TO SPEECH
            # ---------------------
            if decoded_msg.strip() != "":
                tts = gTTS(text=decoded_msg, lang=lang_map[lang_option])
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)

                st.audio(audio_bytes.getvalue(), format="audio/mp3")

        else:
            st.error("First hide the message!")