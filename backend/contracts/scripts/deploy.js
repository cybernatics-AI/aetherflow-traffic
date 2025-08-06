// Deployment script for AetherFlow smart contracts
const { ethers, upgrades } = require("hardhat");

async function main() {
  console.log("Starting AetherFlow smart contracts deployment...");

  // Get the contract factories
  const AetherFlowContractFactory = await ethers.getContractFactory("AetherFlowContractFactory");
  
  // Deploy the contract factory
  console.log("Deploying AetherFlowContractFactory...");
  const factory = await AetherFlowContractFactory.deploy();
  await factory.deployed();
  console.log("AetherFlowContractFactory deployed to:", factory.address);
  
  // Deploy all contracts using the factory
  console.log("Deploying all AetherFlow contracts...");
  const tx = await factory.deployAllContracts();
  const receipt = await tx.wait();
  
  // Get the deployed contract addresses from events
  const aetherTokenDeployedEvent = receipt.events.find(event => event.event === 'AetherTokenDeployed');
  const trafficNFTDeployedEvent = receipt.events.find(event => event.event === 'TrafficNFTDeployed');
  const congestionDerivativesDeployedEvent = receipt.events.find(event => event.event === 'CongestionDerivativesDeployed');
  const aiAgentRegistryDeployedEvent = receipt.events.find(event => event.event === 'AIAgentRegistryDeployed');
  
  // Log the deployed contract addresses
  console.log("AetherToken deployed to:", aetherTokenDeployedEvent.args.contractAddress);
  console.log("TrafficNFT deployed to:", trafficNFTDeployedEvent.args.contractAddress);
  console.log("CongestionDerivatives deployed to:", congestionDerivativesDeployedEvent.args.contractAddress);
  console.log("AIAgentRegistry deployed to:", aiAgentRegistryDeployedEvent.args.contractAddress);
  
  // Save the deployed addresses to a file for future reference
  const fs = require("fs");
  const deploymentInfo = {
    factory: factory.address,
    aetherToken: aetherTokenDeployedEvent.args.contractAddress,
    trafficNFT: trafficNFTDeployedEvent.args.contractAddress,
    congestionDerivatives: congestionDerivativesDeployedEvent.args.contractAddress,
    aiAgentRegistry: aiAgentRegistryDeployedEvent.args.contractAddress,
    network: hre.network.name,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync(
    `deployment-${hre.network.name}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log(`Deployment information saved to deployment-${hre.network.name}.json`);
  
  console.log("Deployment completed successfully!");
}

// Execute the deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
