require("@nomicfoundation/hardhat-toolbox");
require("@nomiclabs/hardhat-ethers");
require("@openzeppelin/hardhat-upgrades");
require("dotenv").config();

// Load environment variables
const HEDERA_PRIVATE_KEY = process.env.HEDERA_PRIVATE_KEY || "";
const HEDERA_ACCOUNT_ID = process.env.HEDERA_ACCOUNT_ID || "";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.17",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    // Local development network
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
    // Hedera Testnet
    testnet: {
      url: "https://testnet.hashio.io/api",
      accounts: HEDERA_PRIVATE_KEY ? [HEDERA_PRIVATE_KEY] : [],
      chainId: 296,
    },
    // Hedera Mainnet
    mainnet: {
      url: "https://mainnet.hashio.io/api",
      accounts: HEDERA_PRIVATE_KEY ? [HEDERA_PRIVATE_KEY] : [],
      chainId: 295,
    }
  },
  etherscan: {
    apiKey: ETHERSCAN_API_KEY
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS !== undefined,
    currency: "USD",
    coinmarketcap: process.env.COINMARKETCAP_API_KEY
  }
};
