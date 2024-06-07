import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# Function to encode the message into the image
def encode_message(image, message):
    image = np.array(image)
    binary_message = ''.join([format(ord(i), '08b') for i in message])
    binary_message += '1111111111111110'  # Delimiter to indicate end of the message

    data_index = 0
    binary_message_length = len(binary_message)

    for values in image:
        for pixel in values:
            r, g, b = format(pixel[0], '08b'), format(pixel[1], '08b'), format(pixel[2], '08b')
            if data_index < binary_message_length:
                pixel[0] = int(r[:-1] + binary_message[data_index], 2)
                data_index += 1
            if data_index < binary_message_length:
                pixel[1] = int(g[:-1] + binary_message[data_index], 2)
                data_index += 1
            if data_index < binary_message_length:
                pixel[2] = int(b[:-1] + binary_message[data_index], 2)
                data_index += 1
            if data_index >= binary_message_length:
                break
        if data_index >= binary_message_length:
            break

    return image

# Function to decode the message from the image
def decode_message(image):
    image = np.array(image)
    binary_data = ""
    delimiter = '1111111111111110'

    for values in image:
        for pixel in values:
            r, g, b = format(pixel[0], '08b'), format(pixel[1], '08b'), format(pixel[2], '08b')
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]

            # Check if the delimiter is found
            if binary_data[-len(delimiter):] == delimiter:
                all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data) - len(delimiter), 8)]
                decoded_message = ''.join([chr(int(byte, 2)) for byte in all_bytes])
                return decoded_message

    return ""

st.title("Steganography Web Application")
st.write("This application allows you to hide a message inside an image and also extract a hidden message from an image.")

option = st.selectbox("Choose an option", ("Encode Message", "Decode Message"))

if option == "Encode Message":
    st.subheader("Encode a message into an image")
    image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    message = st.text_area("Enter the message to hide")

    if st.button("Encode"):
        if image_file and message:
            image = Image.open(image_file)
            encoded_image = encode_message(image, message)
            result_image = Image.fromarray(encoded_image)
            buf = io.BytesIO()
            result_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.image(result_image, caption="Encoded Image", use_column_width=True)
            st.download_button("Download Encoded Image", data=byte_im, file_name="encoded_image.png", mime="image/png")
        else:
            st.error("Please upload an image and enter a message.")

elif option == "Decode Message":
    st.subheader("Decode a message from an image")
    encoded_image_file = st.file_uploader("Upload an encoded image", type=["png", "jpg", "jpeg"])

    if st.button("Decode"):
        if encoded_image_file:
            encoded_image = Image.open(encoded_image_file)
            hidden_message = decode_message(encoded_image)
            if hidden_message:
                st.success(f"Hidden Message: {hidden_message}")
            else:
                st.error("No hidden message found or the message is corrupted.")
        else:
            st.error("Please upload an encoded image.")
