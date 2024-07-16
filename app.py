import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import qrcode
from PIL import Image
from io import BytesIO

# Replace with your own Etherscan API key
ETHERSCAN_API_KEY = '72ZYQBUT6BKEG7TTJ3EDEV1TW7WEKWKW6I'

# Smart contract addresses
SMART_CONTRACTS = {
    'BANANA': '0x890714f0269861582be8cbad83aaa3e059eb0b22',
    'DRAGON FRUIT': '0x0E8c2758bd0aBd12020FC626Aa703f4a70519D10',
    'PAPAYA': '0x93688eB37df5479d15034F9d0e20F07c3eAd3Ad1'
}

# Detailed mapping of Ethereum addresses to supply chain roles
ADDRESS_TO_ROLE = {
    '0xd5523fdb700a9e836dcaf1110e365e803eae71aa': 'Produsen Banana',
    '0x488fd778a4c1a866a6ca6c05a4e1e00d8cf7f8da': 'Produsen Dragon Fruit',
    '0xbd4be1bd11cd18513b3dd44cf2ad7f1c9b762c8a': 'Produsen Papaya',
    '0x81c1fabd59c68c5b919a547b951a2a600c979fba': 'Distributor A',
    '0xbe886552107a1c26eea37c0af1c6108e0b5f35ab': 'Distributor B',
    '0x49C15E463C690098d149F2fb90117fE706100d43': 'Supermarket A',
    '0x2722199d3d31088d74d9c8d864ef806db4cc5f76': 'Supermarket B',
    '0x24d61ba1903f4c39d80f407a8696e4adf0081246': 'Retail 1',
    '0xca0c515f6e6d75306c0e312ee11d0873d6133866': 'Retail 2',
}

def get_transactions(token_address, api_key):
    url = f'https://api-sepolia.etherscan.io/api?module=account&action=tokentx&contractaddress={token_address}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

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

# Load CSS file
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load JavaScript file
with open("script.js", "r", encoding="utf-8") as f:
    st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

st.title('Etherscan Token Transactions Viewer')

# Dropdown menu for selecting smart contract
contract_options = ['None'] + list(SMART_CONTRACTS.keys())
selected_contract = st.selectbox('Select a Smart Contract', contract_options)
token_address = SMART_CONTRACTS.get(selected_contract) if selected_contract != 'None' else None

if token_address:
    if st.button('Show Transaction Details'):
        transactions_data = get_transactions(token_address, ETHERSCAN_API_KEY)

        if transactions_data and transactions_data.get('status') == '1':
            transactions = transactions_data['result']
            st.write(f"Total Transactions: {len(transactions)}")

            # Prepare data for the chart
            transactions_df = pd.DataFrame(transactions)
            transactions_df['timeStamp'] = pd.to_datetime(transactions_df['timeStamp'], unit='s')
            transactions_df['value'] = transactions_df['value'].astype(float)

            # Rename 'from' and 'to' columns to avoid conflicts
            transactions_df.rename(columns={'from': 'from_address', 'to': 'to_address'}, inplace=True)

            # Format the timestamp
            transactions_df['formatted_timeStamp'] = transactions_df['timeStamp'].dt.strftime('%b-%d-%Y %I:%M:%S %p UTC')

            # Map addresses to supply chain roles
            transactions_df['from_role'] = transactions_df['from_address'].map(ADDRESS_TO_ROLE).fillna('Unknown')
            transactions_df['to_role'] = transactions_df['to_address'].map(ADDRESS_TO_ROLE).fillna('Unknown')

            # Generate QR Code for the token address
            etherscan_url = f"https://sepolia.etherscan.io/token/{token_address}"
            qr_code = generate_qr_code(etherscan_url, size=200)
            buffer_qr = BytesIO()
            qr_code.save(buffer_qr, format="PNG")
            
            # Aggregate the token holdings by 'to_role'
            holders_df = transactions_df.groupby('to_role')['value'].sum().reset_index()
            holders_df = holders_df.rename(columns={'to_role': 'Role', 'value': 'Total Tokens'})

            # Plotly pie chart
            fig = px.pie(holders_df, values='Total Tokens', names='Role', title='Token Distribution among Holders')
            
            # Create two columns for QR Code and Pie Chart
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(buffer_qr.getvalue(), use_column_width=True)

            with col2:
                st.plotly_chart(fig, use_container_width=True)

            # Display transaction details
            st.markdown('<div class="stHeader">Transaction Details</div>', unsafe_allow_html=True)
            for tx in transactions_df.itertuples():
                st.markdown(f'''
                    <div class="stCard">
                        <h2>Transaction Hash: {tx.hash}</h2>
                        <p>From: {tx.from_role}</p>
                        <p>To: {tx.to_role}</p>
                        <p>Value: {str(tx.value).rstrip('0').rstrip('.') + ' buah'}</p>
                        <p>Token Symbol: {tx.tokenSymbol}</p>
                        <p>Timestamp: {tx.formatted_timeStamp}</p>
                    </div>
                ''', unsafe_allow_html=True)

elif selected_contract == 'None':
    st.info('Please select a smart contract to view transaction details.')
else:
    st.error('Invalid token address selected.')
