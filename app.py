import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# Replace with your own Etherscan API key
ETHERSCAN_API_KEY = '72ZYQBUT6BKEG7TTJ3EDEV1TW7WEKWKW6I'

# Smart contract addresses
SMART_CONTRACTS = {
    'BANANA': '0x890714f0269861582be8cbad83aaa3e059eb0b22',
    'DRAGON FRUIT': '0x...dragon_fruit_address...',
    'PAPAYA': '0x...papaya_address...'
}

def get_transactions(token_address, api_key):
    url = f'https://api-sepolia.etherscan.io/api?module=account&action=tokentx&contractaddress={token_address}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

st.title('Etherscan Token Transactions Viewer')

# Dropdown menu for selecting smart contract
selected_contract = st.selectbox('Select a Smart Contract', list(SMART_CONTRACTS.keys()))
token_address = SMART_CONTRACTS[selected_contract]

transactions_data = get_transactions(token_address, ETHERSCAN_API_KEY)

if transactions_data and transactions_data.get('status') == '1':
    transactions = transactions_data['result']
    st.write(f"Total Transactions: {len(transactions)}")

    # Prepare data for the chart
    transactions_df = pd.DataFrame(transactions)
    transactions_df['timeStamp'] = pd.to_datetime(transactions_df['timeStamp'], unit='s')
    transactions_df['value'] = transactions_df['value'].astype(float)

    # Display transaction details
    for tx in transactions:
        st.write(f"Hash: {tx['hash']}")
        st.write(f"From: {tx['from']}")
        st.write(f"To: {tx['to']}")
        st.write(f"Value: {tx['value']}")
        st.write(f"Token Symbol: {tx['tokenSymbol']}")
        st.write(f"Timestamp: {tx['timeStamp']}")
        st.write('---')

    # Aggregate the token holdings by 'to' address
    holders_df = transactions_df.groupby('to')['value'].sum().reset_index()
    holders_df = holders_df.rename(columns={'to': 'Holder', 'value': 'Total Tokens'})

    # Plotly pie chart
    fig_pie = px.pie(holders_df, values='Total Tokens', names='Holder', title='Token Distribution Among Holders')
    st.plotly_chart(fig_pie)

else:
    st.error('Failed to retrieve transactions or no transactions found.')
