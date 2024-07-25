import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import qrcode
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
import pytz

# Set page title, tab title, and icon
st.set_page_config(page_title="Supply Chain with Blockchain", page_icon="🔗")

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
    '0x49c15e463c690098d149f2fb90117fe706100d43': 'Supermarket A',
    '0x2722199d3d31088d74d9c8d864ef806db4cc5f76': 'Supermarket B',
    '0x24d61ba1903f4c39d80f407a8696e4adf0081246': 'Retail 1',
    '0xca0c515f6e6d75306c0e312ee11d0873d6133866': 'Retail 2',
    '0x13a4667ce9a4dcb01b16215fdfbf145622fc3eb5': 'Restaurant A',
    '0x3408c665f2298d7cafcbd4350d67d2833264b294': 'Restaurant B',
    '0x0000000000000000000000000000000000000000': 'Minting/Burn',
}

# Smart contract creators and their proof hashes
CONTRACT_CREATORS = {
    'BANANA': {
        'creator': 'Produsen Banana',
        'hash': '0x0fb39897123a03c085456a7cc56bd98d516e6ba8249c5d1bef17256da6e82c4d'
    },
    'DRAGON FRUIT': {
        'creator': 'Produsen Dragon Fruit',
        'hash': '0x4d24a4856a563df259cbcdc2a6b61fa8c097998831af4af93ae4e94776c7ea89'
    },
    'PAPAYA': {
        'creator': 'Produsen Papaya',
        'hash': '0xf3fda77d6a88a8e54973632bd943de63d8e913dddf35ddd5b307afc42965c547'
    }
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

# Function to convert UTC to WIB
def convert_to_wib(utc_time):
    utc = pytz.utc
    wib = pytz.timezone('Asia/Jakarta')
    utc_dt = utc.localize(utc_time)
    wib_dt = utc_dt.astimezone(wib)
    formatted_time = wib_dt.strftime('%b-%d-%Y %I:%M:%S %p')
    return formatted_time

# Load CSS file
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load JavaScript file
with open("script.js", "r", encoding="utf-8") as f:
    st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

# Page title
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

             # Display smart contract creator information
            creator_info = CONTRACT_CREATORS.get(selected_contract, {})
            st.write(f"**Creator Smart Contract {selected_contract}**")
            st.write(f"- **Creator:** {creator_info.get('creator')}")
            st.write(f"- **Proof Hash:** {creator_info.get('hash')}")
            st.write(f"")
            st.write(f"")

            # Prepare data for the chart
            transactions_df = pd.DataFrame(transactions)
            transactions_df['timeStamp'] = pd.to_datetime(transactions_df['timeStamp'], unit='s')
            transactions_df['value'] = transactions_df['value'].astype(float) / 10**1  # Adjust for 1 decimal place

            # Rename 'from' and 'to' columns to avoid conflicts
            transactions_df.rename(columns={'from': 'from_address', 'to': 'to_address'}, inplace=True)

            # Normalize the case of addresses
            transactions_df['from_address'] = transactions_df['from_address'].str.lower()
            transactions_df['to_address'] = transactions_df['to_address'].str.lower()

            # Convert timestamp to WIB and format it
            transactions_df['formatted_timeStamp'] = transactions_df['timeStamp'].apply(convert_to_wib)

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
            st.markdown('<div class="stTransactionDetails">', unsafe_allow_html=True)
            for tx in transactions_df.itertuples():
                value_display = "{:,.1f} buah".format(tx.value)  # Format the value with commas and one decimal place
                transaction_link = f"https://sepolia.etherscan.io/tx/{tx.hash}"
                
                # Fetch transaction details for block confirmations
                block_details_url = f'https://api-sepolia.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx.hash}&apikey={ETHERSCAN_API_KEY}'
                block_details_response = requests.get(block_details_url)
                block_details = block_details_response.json()

                block_number = block_details['result'].get('blockNumber')
                latest_block_url = f'https://api-sepolia.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={ETHERSCAN_API_KEY}'
                latest_block_response = requests.get(latest_block_url)
                latest_block = latest_block_response.json()

                if block_number and latest_block.get('result'):
                    block_number = int(block_number, 16)
                    latest_block_number = int(latest_block['result'], 16)
                    block_confirmations = latest_block_number - block_number
                else:
                    block_confirmations = 'N/A'

                # Use expander for QR code
                with st.expander(f"Transaction Hash: {tx.hash}"):
                    qr_code_tx = generate_qr_code(transaction_link, size=200)
                    buffer_tx = BytesIO()
                    qr_code_tx.save(buffer_tx, format="PNG")
                    st.image(buffer_tx.getvalue(), use_column_width=True)
                    st.markdown(f'<a href="{transaction_link}" target="_blank">{tx.hash}</a>', unsafe_allow_html=True)
                    st.write(f"Timestamp: {tx.formatted_timeStamp}")
                    st.write(f"From: {tx.from_role}")
                    st.write(f"To: {tx.to_role}")
                    st.write(f"Value: {value_display}")
                    st.write(f"Block Confirmations: {block_confirmations}")

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.write('No transactions found or an error occurred.')
