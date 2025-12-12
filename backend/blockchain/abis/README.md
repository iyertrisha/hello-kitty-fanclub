# Contract ABIs

This directory contains the compiled contract ABIs (Application Binary Interfaces).

## After Compilation

After running `npm run compile`, copy the ABI file here:

```powershell
# PowerShell command
Copy-Item artifacts\contracts\KiranaLedger.sol\KiranaLedger.json -Destination abis\KiranaLedger.json
```

The ABI file is required for the Python blockchain service to interact with the smart contract.



