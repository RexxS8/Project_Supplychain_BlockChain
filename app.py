import streamlit as st
import qrcode
from io import BytesIO
import requests
from PIL import Image
import matplotlib.pyplot as plt

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

# Address roles
ADDRESS_TO_ROLE = {
    '0xd5523fdb700a9e836dcaf1110e365e803eae71aa': 'Produsen Banana',
    '0x488fd778a4c1a866a6ca6c05a4e1e00d8cf7f8da': 'Produsen Dragon Fruit',
    '0xbd4be1bd11cd18513b3dd44cf2ad7f1c9b762c8a': 'Produsen Papaya',
    '0x81c1fabd59c68c5b919a547b951a2a600c979fba': 'Distributor A',
    '0xbe886552107a1c26eea37c0af1c6108e0b5f35ab': 'Distributor B',
    '0x49c15e463c690098d149f2fb90117fe706100d43': 'Supermarket A',
    '0x2722199d3d31088d74d9c8d864ef806db4cc5f76': 'Supermarket B',
    '0x24d61ba1903f4c39d80f407a8696e4adf0081246': 'Retail 1',
    '0xca0c515f6e6d75306c0e312ee11d0873d6133866': 'Retail 2',
    '0x13a4667ce9a4dcb01b16215fdfbf145622fc3eb5': 'Restaurant A',
    '0x3408c665f2298d7cafcbd4350d67d2833264b294': 'Restaurant B',
    '0x0000000000000000000000000000000000000000': 'Minting/Burn',
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

def display_pie_chart(data):
    labels = [ADDRESS_TO_ROLE.get(address, address) for address in data.keys()]
    sizes = data.values()
    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    st.pyplot(plt)

# Example token holder data for pie chart demonstration
EXAMPLE_HOLDER_DATA = {
    '0xbD4bE1bD11CD18513b3dd44CF2aD7F1c9b762C8a': 385,
    '0xbE886552107a1C26EEA37C0af1C6108e0b5f35ab': 330,
    '0x81C1faBd59c68C5B919a547b951a2a600c979fBA': 205,
    '0x13a4667Ce9A4DcB01b16215FDfbF145622FC3Eb5': 45,
    '0xCa0C515f6E6D75306C0E312EE11d0873d6133866': 35
}

# Page title
st.title('Token Holders Viewer for Supply Chain Blockchain')

# Dropdown menu for selecting smart contract
contract_options = ['None'] + list(SMART_CONTRACTS.keys())
selected_contract = st.selectbox('Select a Smart Contract', contract_options)

# Button to confirm selection
if st.button("View Details") and selected_contract != 'None':
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
    
    # Display example pie chart based on EXAMPLE_HOLDER_DATA
    st.write("**Token Holder Distribution Pie Chart**")
    display_pie_chart(EXAMPLE_HOLDER_DATA)
else:
    st.write("Please select a contract and press 'View Details'.")
