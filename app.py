import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import qrcode
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
import pytz
import base64

# Set page title, tab title, and icon
st.set_page_config(page_title="Supply Chain with Blockchain", page_icon="🔗")

# Replace with your own Etherscan API key
ETHERSCAN_API_KEY = 'import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import qrcode
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
import pytz
import base64

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

# Semua fungsi utility tetap sama sesuai kode awal
def get_transactions(token_address, api_key):
    url = f'https://api-sepolia.etherscan.io/api?module=account&action=tokentx&contractaddress={token_address}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_token_balance(contract_address, wallet_address, api_key):
    url = f'https://api-sepolia.etherscan.io/api?module=account&action=tokenbalance&contractaddress={contract_address}&address={wallet_address}&tag=latest&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('status') == '1':
        balance = response.json().get('result', '0')
        return float(balance)
    else:
        return 0

def convert_to_wib(utc_time):
    utc = pytz.utc
    wib = pytz.timezone('Asia/Jakarta')
    utc_dt = utc.localize(utc_time)
    wib_dt = utc_dt.astimezone(wib)
    formatted_time = wib_dt.strftime('%b-%d-%Y %I:%M:%S %p')
    return formatted_time

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
    img = img.resize((size, size))
    return img

# Load CSS file
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load JavaScript file
with open("script.js", "r", encoding="utf-8") as f:
    st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

# Streamlit main content
st.title('Etherscan Token Transactions Viewer')

contract_options = ['None'] + list(SMART_CONTRACTS.keys())
selected_contract = st.selectbox('Select a Smart Contract', contract_options)
token_address = SMART_CONTRACTS.get(selected_contract) if selected_contract != 'None' else None

if token_address:
    if st.button('Show Transaction / Refresh Transaction'):
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

            # Data preparation
            transactions_df = pd.DataFrame(transactions)
            transactions_df['timeStamp'] = pd.to_datetime(transactions_df['timeStamp'], unit='s')

            # Ubah nilai menjadi float dengan desimal satu tempat (contoh: 5300 -> 530.0)
            transactions_df['value'] = (transactions_df['value'].astype(float) / 10).round(1)

            # Normalize address case
            transactions_df['from_address'] = transactions_df['from'].str.lower()
            transactions_df['to_address'] = transactions_df['to'].str.lower()

            # Map roles to addresses
            transactions_df['from_role'] = transactions_df['from_address'].map(ADDRESS_TO_ROLE).fillna('Unknown')
            transactions_df['to_role'] = transactions_df['to_address'].map(ADDRESS_TO_ROLE).fillna('Unknown')

            # Fetch balances and map to roles
            unique_addresses = transactions_df['to_address'].unique()
            address_to_balance = {
                address: round(get_token_balance(token_address, address, ETHERSCAN_API_KEY) / 10, 1) for address in unique_addresses
            }

            # Summarize balances by role
            role_balances = (
                pd.DataFrame(list(address_to_balance.items()), columns=['to_address', 'balance'])
                .assign(role=lambda df: df['to_address'].map(ADDRESS_TO_ROLE).fillna('Unknown'))
                .groupby('role')['balance']
                .sum()
                .reset_index()
                .rename(columns={'role': 'Role', 'balance': 'Total Tokens'})
            )

            # Pastikan kolom Total Tokens berbentuk float dengan 1 desimal
            role_balances['Total Tokens'] = role_balances['Total Tokens'].astype(float).round(1)

            # Plotly pie chart
            fig = px.pie(role_balances, values='Total Tokens', names='Role', title='Token Distribution')

            # Columns for QR Code and Pie Chart
            col1, col2 = st.columns([1, 2])

            with col1:
                etherscan_url = f"https://sepolia.etherscan.io/token/{token_address}"
                qr_code = generate_qr_code(etherscan_url)
                buffer_qr = BytesIO()
                qr_code.save(buffer_qr, format="PNG")
                st.image(buffer_qr.getvalue(), use_column_width=True)

            with col2:
                st.plotly_chart(fig, use_container_width=True)

            # Display transaction details
            st.markdown('<div style="text-align: center; font-size: 24px; font-weight: bold; color: white; background-color: purple; padding: 10px; border-radius: 8px;">Transaction Details</div>', unsafe_allow_html=True)
            st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)

            for tx in transactions_df.itertuples():
                value_display = f"{tx.value:,.1f} buah"
                transaction_link = f"https://sepolia.etherscan.io/tx/{tx.hash}"

                # Generate QR Code for transaction link
                qr_code = generate_qr_code(transaction_link, size=100)
                buffer_qr = BytesIO()
                qr_code.save(buffer_qr, format="PNG")

                # Fetch block confirmations
                block_details_url = f'https://api-sepolia.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx.hash}&apikey={ETHERSCAN_API_KEY}'
                block_details_response = requests.get(block_details_url)
                block_details = block_details_response.json()
                block_number = block_details['result'].get('blockNumber') if block_details.get('result') else None

                if block_number:
                    latest_block_url = f'https://api-sepolia.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={ETHERSCAN_API_KEY}'
                    latest_block_response = requests.get(latest_block_url)
                    latest_block = latest_block_response.json()
                    latest_block_number = int(latest_block['result'], 16) if 'result' in latest_block else None
                    block_confirmations = (
                        latest_block_number - int(block_number, 16) if latest_block_number and block_number else 'Block Confirmed'
                    )
                else:
                    block_confirmations = 'Block Confirmed'

                # Render transaction details in card-like format with fixed hash box
                st.markdown(f'''
                <div style="background-color: #f9f9f9; padding: 20px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #ddd;">
                    <h3 style="font-size: 16px; word-wrap: break-word; overflow-wrap: break-word; margin-bottom: 5px;">Transaction Hash:</h3>
                    <p style="font-size: 20px; word-wrap: break-word; overflow-wrap: break-word; color: blue; margin: 10;">
                        <a href="{transaction_link}" target="_blank" style="text-decoration: none; color: blue;">{tx.hash}</a>
                    </p>
                    <p><strong>From:</strong> {tx.from_role}</p>
                    <p><strong>To:</strong> {tx.to_role}</p>
                    <p><strong>Value:</strong> {value_display}</p>
                    <p><strong>Token Symbol:</strong> {tx.tokenSymbol}</p>
                    <p><strong>Time:</strong> {convert_to_wib(tx.timeStamp)}</p>
                    <p><strong>Confirmations:</strong> {block_confirmations}</p>
                    <img src="data:image/png;base64,{base64.b64encode(buffer_qr.getvalue()).decode()}" alt="QR Code" style="display: block; margin: 10px auto;"/>
                </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
'

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

# Semua fungsi utility tetap sama sesuai kode awal
def get_transactions(token_address, api_key):
    url = f'https://api-sepolia.etherscan.io/api?module=account&action=tokentx&contractaddress={token_address}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_token_balance(contract_address, wallet_address, api_key):
    url = f'https://api-sepolia.etherscan.io/api?module=account&action=tokenbalance&contractaddress={contract_address}&address={wallet_address}&tag=latest&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('status') == '1':
        balance = response.json().get('result', '0')
        return float(balance)
    else:
        return 0

def convert_to_wib(utc_time):
    utc = pytz.utc
    wib = pytz.timezone('Asia/Jakarta')
    utc_dt = utc.localize(utc_time)
    wib_dt = utc_dt.astimezone(wib)
    formatted_time = wib_dt.strftime('%b-%d-%Y %I:%M:%S %p')
    return formatted_time

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
    img = img.resize((size, size))
    return img

# Load CSS file
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load JavaScript file
with open("script.js", "r", encoding="utf-8") as f:
    st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

# Streamlit main content
st.title('Etherscan Token Transactions Viewer')

contract_options = ['None'] + list(SMART_CONTRACTS.keys())
selected_contract = st.selectbox('Select a Smart Contract', contract_options)
token_address = SMART_CONTRACTS.get(selected_contract) if selected_contract != 'None' else None

if token_address:
    if st.button('Show Transaction / Refresh Transaction'):
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

            # Data preparation
            transactions_df = pd.DataFrame(transactions)
            transactions_df['timeStamp'] = pd.to_datetime(transactions_df['timeStamp'], unit='s')

            # Ubah nilai menjadi float dengan desimal satu tempat (contoh: 5300 -> 530.0)
            transactions_df['value'] = (transactions_df['value'].astype(float) / 10).round(1)

            # Normalize address case
            transactions_df['from_address'] = transactions_df['from'].str.lower()
            transactions_df['to_address'] = transactions_df['to'].str.lower()

            # Map roles to addresses
            transactions_df['from_role'] = transactions_df['from_address'].map(ADDRESS_TO_ROLE).fillna('Unknown')
            transactions_df['to_role'] = transactions_df['to_address'].map(ADDRESS_TO_ROLE).fillna('Unknown')

            # Fetch balances and map to roles
            unique_addresses = transactions_df['to_address'].unique()
            address_to_balance = {
                address: round(get_token_balance(token_address, address, ETHERSCAN_API_KEY) / 10, 1) for address in unique_addresses
            }

            # Summarize balances by role
            role_balances = (
                pd.DataFrame(list(address_to_balance.items()), columns=['to_address', 'balance'])
                .assign(role=lambda df: df['to_address'].map(ADDRESS_TO_ROLE).fillna('Unknown'))
                .groupby('role')['balance']
                .sum()
                .reset_index()
                .rename(columns={'role': 'Role', 'balance': 'Total Tokens'})
            )

            # Pastikan kolom Total Tokens berbentuk float dengan 1 desimal
            role_balances['Total Tokens'] = role_balances['Total Tokens'].astype(float).round(1)

            # Plotly pie chart
            fig = px.pie(role_balances, values='Total Tokens', names='Role', title='Token Distribution')

            # Columns for QR Code and Pie Chart
            col1, col2 = st.columns([1, 2])

            with col1:
                etherscan_url = f"https://sepolia.etherscan.io/token/{token_address}"
                qr_code = generate_qr_code(etherscan_url)
                buffer_qr = BytesIO()
                qr_code.save(buffer_qr, format="PNG")
                st.image(buffer_qr.getvalue(), use_column_width=True)

            with col2:
                st.plotly_chart(fig, use_container_width=True)

            # Display transaction details
            st.markdown('<div style="text-align: center; font-size: 24px; font-weight: bold; color: white; background-color: purple; padding: 10px; border-radius: 8px;">Transaction Details</div>', unsafe_allow_html=True)
            st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)

            for tx in transactions_df.itertuples():
                value_display = f"{tx.value:,.1f} buah"
                transaction_link = f"https://sepolia.etherscan.io/tx/{tx.hash}"

                # Generate QR Code for transaction link
                qr_code = generate_qr_code(transaction_link, size=100)
                buffer_qr = BytesIO()
                qr_code.save(buffer_qr, format="PNG")

                # Fetch block confirmations
                block_details_url = f'https://api-sepolia.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx.hash}&apikey={ETHERSCAN_API_KEY}'
                block_details_response = requests.get(block_details_url)
                block_details = block_details_response.json()
                block_number = block_details['result'].get('blockNumber') if block_details.get('result') else None

                if block_number:
                    latest_block_url = f'https://api-sepolia.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={ETHERSCAN_API_KEY}'
                    latest_block_response = requests.get(latest_block_url)
                    latest_block = latest_block_response.json()
                    latest_block_number = int(latest_block['result'], 16) if 'result' in latest_block else None
                    block_confirmations = (
                        latest_block_number - int(block_number, 16) if latest_block_number and block_number else 'Block Confirmed'
                    )
                else:
                    block_confirmations = 'Block Confirmed'

                # Render transaction details in card-like format with fixed hash box
                st.markdown(f'''
                <div style="background-color: #f9f9f9; padding: 20px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #ddd;">
                    <h3 style="font-size: 16px; word-wrap: break-word; overflow-wrap: break-word; margin-bottom: 5px;">Transaction Hash:</h3>
                    <p style="font-size: 20px; word-wrap: break-word; overflow-wrap: break-word; color: blue; margin: 10;">
                        <a href="{transaction_link}" target="_blank" style="text-decoration: none; color: blue;">{tx.hash}</a>
                    </p>
                    <p><strong>From:</strong> {tx.from_role}</p>
                    <p><strong>To:</strong> {tx.to_role}</p>
                    <p><strong>Value:</strong> {value_display}</p>
                    <p><strong>Token Symbol:</strong> {tx.tokenSymbol}</p>
                    <p><strong>Time:</strong> {convert_to_wib(tx.timeStamp)}</p>
                    <p><strong>Confirmations:</strong> {block_confirmations}</p>
                    <img src="data:image/png;base64,{base64.b64encode(buffer_qr.getvalue()).decode()}" alt="QR Code" style="display: block; margin: 10px auto;"/>
                </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
