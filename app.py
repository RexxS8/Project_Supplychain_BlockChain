import streamlit as st
import qrcode
from io import BytesIO
import requests
from PIL import Image

# Set page title, tab title, and icon
st.set_page_config(page_title="Supply Chain with Blockchain", page_icon="🔗")

# Smart contract holder and pie chart links
SMART_CONTRACTS = {
    'BANANA': {
        'holders': 'https://sepolia.etherscan.io/token/0x890714f0269861582be8cbad83aaa3e059eb0b22#balances',
        'pie_chart': 'https://sepolia.etherscan.io/token/tokenholderchart/0x890714f0269861582be8cbad83aaa3e059eb0b22'
    },
    'DRAGON FRUIT': {
        'holders': 'https://sepolia.etherscan.io/token/0x0e8c2758bd0abd12020fc626aa703f4a70519d10#balances',
        'pie_chart': 'https://sepolia.etherscan.io/token/tokenholderchart/0x0e8c2758bd0abd12020fc626aa703f4a70519d10'
    },
    'PAPAYA': {
        'holders': 'https://sepolia.etherscan.io/token/0x93688eb37df5479d15034f9d0e20f07c3ead3ad1#balances',
        'pie_chart': 'https://sepolia.etherscan.io/token/tokenholderchart/0x93688eb37df5479d15034f9d0e20f07c3ead3ad1'
    }
}

def generate_qr_code(data, size=200):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img = img.resize((size, size))  # Resize QR Code to desired size
    return img

def fetch_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# Page title
st.title('Token Holders Viewer for Supply Chain Blockchain')

# Dropdown menu for selecting smart contract
contract_options = ['None'] + list(SMART_CONTRACTS.keys())
selected_contract = st.selectbox('Select a Smart Contract', contract_options)

if selected_contract != 'None':
    # Get selected contract details
    token_holder_url = SMART_CONTRACTS[selected_contract]['holders']
    pie_chart_url = SMART_CONTRACTS[selected_contract]['pie_chart']
    
    # Generate and display QR Code for token holder link
    qr_code = generate_qr_code(token_holder_url, size=200)
    buffer_qr = BytesIO()
    qr_code.save(buffer_qr, format="PNG")
    
    st.write(f"**Holder Information for {selected_contract}**")
    st.markdown(f"[View Token Holders on Etherscan]({token_holder_url})")
    st.image(buffer_qr.getvalue(), use_column_width=True)
    st.write("Scan the QR code to view the token holders on Etherscan.")
    
    # Fetch and display pie chart for the selected contract
    st.write("**Token Holder Distribution Pie Chart**")
    try:
        pie_chart_img = fetch_image_from_url(pie_chart_url)
        st.image(pie_chart_img, caption="Token Holder Pie Chart", use_column_width=True)
    except:
        st.write("Unable to fetch the pie chart. Please check the link manually.")
