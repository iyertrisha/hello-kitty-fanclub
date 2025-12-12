import hre from "hardhat";
import fs from "fs";
import path from "path";

async function main() {
  try {
    console.log("\n🚀 Starting deployment...\n");

    // Get the deployer account
    const [deployer] = await hre.ethers.getSigners();
    console.log("📝 Deploying contracts with account:", deployer.address);

    // Get account balance
    const balance = await hre.ethers.provider.getBalance(deployer.address);
    console.log("💰 Account balance:", hre.ethers.formatEther(balance), "ETH\n");

    // Get the contract factory
    console.log("🔨 Getting contract factory for KiranaLedger...");
    const KiranaLedger = await hre.ethers.getContractFactory("KiranaLedger");

    // Deploy the contract
    console.log("⏳ Deploying contract...");
    const kiranaLedger = await KiranaLedger.deploy();

    // Wait for deployment to complete
    await kiranaLedger.waitForDeployment();

    // Get the deployed contract address
    const contractAddress = await kiranaLedger.getAddress();

    console.log("\n✅ Deployment successful!\n");
    console.log("═══════════════════════════════════════════════════");
    console.log("Contract Name:    KiranaLedger");
    console.log("Contract Address:", contractAddress);
    console.log("Deployer Address:", deployer.address);
    console.log("Network:         ", hre.network.name);
    console.log("Chain ID:        ", hre.network.config.chainId);
    console.log("═══════════════════════════════════════════════════\n");

    // Save contract address to file
    const addressData = {
      contractAddress: contractAddress,
      deployer: deployer.address,
      network: hre.network.name,
      chainId: hre.network.config.chainId,
      deployedAt: new Date().toISOString(),
    };

    const outputPath = path.join(process.cwd(), "deployed_address.json");
    fs.writeFileSync(outputPath, JSON.stringify(addressData, null, 2));
    console.log("📄 Contract address saved to:", outputPath);

    // If on Polygon Amoy, provide explorer link
    if (hre.network.name === "polygonAmoy") {
      console.log("\n🔍 View on PolygonScan Amoy:");
      console.log(`   https://amoy.polygonscan.com/address/${contractAddress}\n`);
    }

    return contractAddress;
  } catch (error) {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  }
}

// Execute main function
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });



