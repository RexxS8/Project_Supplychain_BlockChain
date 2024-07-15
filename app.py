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

# Mapping of Ethereum addresses to supply chain roles
ADDRESS_TO_ROLE = {
    '0x...farmer_address...': 'Farmer',
    '0x...aggregator_address...': 'Aggregator',
    '0x...distributor_address...': 'Distributor',
    '0x...consumer_address...': 'Consumer',
    # Add more mappings as needed
}

def get_transactions(token_address, api_key):
    url = f'https://api-sepolia.etherscan.io/api?module=account&action=tokentx&contractaddress={token_address}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

# Load CSS file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title('Etherscan Token Transactions Viewer')

# Dropdown menu for selecting smart contract
selected_contract = st.selectbox('Select a Smart Contract', list(SMART_CONTRACTS.keys()))
token_address = SMART_CONTRACTS.get(selected_contract)

if token_address:
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
        transactions_df['from_address'] = transactions_df['from_address'].map(ADDRESS_TO_ROLE).fillna(transactions_df['from_address'])
        transactions_df['to_address'] = transactions_df['to_address'].map(ADDRESS_TO_ROLE).fillna(transactions_df['to_address'])

        # Display transaction details
        for tx in transactions_df.itertuples():
            st.write(f"Hash: {tx.hash}")
            st.write(f"From: {tx.from_address} (Role: {ADDRESS_TO_ROLE.get(tx.from_address, 'Unknown')})")
            st.write(f"To: {tx.to_address} (Role: {ADDRESS_TO_ROLE.get(tx.to_address, 'Unknown')})")
            st.write(f"Value: {tx.value}")
            st.write(f"Token Symbol: {tx.tokenSymbol}")
            st.write(f"Timestamp: {tx.formatted_timeStamp}")
            st.write('---')

        # Aggregate the token holdings by 'to_address'
        holders_df = transactions_df.groupby('to_address')['value'].sum().reset_index()
        holders_df = holders_df.rename(columns={'to_address': 'Role', 'value': 'Total Tokens'})

        # Plotly pie chart
        fig_pie = px.pie(holders_df, values='Total Tokens', names='Role', title='Token Distribution Among Holders')
        st.plotly_chart(fig_pie)

        # Generate QR code for the selected contract
        etherscan_url = f"https://sepolia.etherscan.io/token/{token_address}"
        qr_code_img = generate_qr_code(etherscan_url)
        buffer = BytesIO()
        qr_code_img.save(buffer, format="PNG")
        st.image(buffer.getvalue(), caption=f'QR Code for {selected_contract}', use_column_width=True)

    else:
        st.error('Failed to retrieve transactions or no transactions found.')

else:
    st.warning("Please select a Smart Contract from the dropdown to view transactions.")
