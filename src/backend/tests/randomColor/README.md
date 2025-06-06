# Setup

1. New account on supabase and new project and new table named as `colors` with column names as `hex_code` and `description`.
2. Create a metamask wallet with sepolia testnet and get free coins from here: https://cloud.google.com/application/web3/faucet/ethereum/sepolia
3. Go to Remix IDE (https://remix.ethereum.org/).
Create a new file ColorRegistry.sol and paste the code.
Go to the "Solidity Compiler" tab, select a compatible compiler version (e.g., 0.8.9 or newer), and click "Compile ColorRegistry.sol".
Go to the "Deploy & Run Transactions" tab.
Environment: Select "Injected Provider - MetaMask". MetaMask will pop up asking you to connect. Make sure MetaMask is set to the Sepolia Testnet.
Account: Your MetaMask account (with Sepolia ETH) should be selected.
Contract: Select ColorRegistry.
Click "Deploy". MetaMask will ask you to confirm the transaction (pay gas fees).
Once deployed, you'll see the deployed contract address at the bottom of the "Deploy & Run Transactions" tab. Copy this address.
Also, go back to the "Solidity Compiler" tab, and under "Contract: ColorRegistry", click the "ABI" button to copy the contract's ABI. Save this ABI and paste it where it needs to be pasted in app.py.
4. Signup on https://developer.metamask.io/ and get your api key and then paste that api key in the `.env` as `METAMASK_API_KEY`.
5. add your wallet address as contact address in the configure section of the api key on the metamask developer portal and then also set it as the `CONTRACT_ADDRESS` and `BACKEND_WALLET_ADDRESS`.
6. Open MetaMask and make sure you have the correct account selected (0xa29...).
Click the three dots (⋮) menu.
Select "Account details".
Click the "Show private key" button.
You will have to enter your MetaMask password to reveal it.
Copy the long, 64-character hexadecimal string. It will NOT start with 0x.
Paste this correct private key into your .env file for `BACKEND_WALLET_PRIVATE_KEY`.
7. Go to your Supabase project dashboard.
Go to Project Settings (the gear icon ⚙️).
Click on "API" in the side menu.
Scroll down to the "Project API keys" section.
Find the key labeled service_role. It will say "(secret)" next to it.
Click "Copy" and paste this key into your .env file. It's a much longer JWT.

# RUN

1. Run the app.py file.
2. To check your results, run the `endpoint_checker.py` file.
3. If the output of app.py is like:
```text
INFO in app: Saved to Supabase: ('data', [{'id': 8, 'created_at': '2025-06-06T22:05:34.051009+00:00', 'hex_code': '#940c9a', 'description': 'A regal and mysterious amethyst purple.'}])
INFO in app: Sent to Blockchain, TxHash: cfb0626d8d882e35aae23000f4ef7709ddbae09fdf93e197a43ead695a485f0c
```
you have successfully saved the color to Supabase and sent it to the blockchain.
4. Copy the transaction hash (0x...) from your Flask terminal and
go to the Sepolia Etherscan: https://sepolia.etherscan.io/ and paste the transaction hash in the search bar and look for the transaction.