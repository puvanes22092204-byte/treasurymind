"""Blockchain Audit Trail - immutable on-chain logging via Polygon testnet."""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "https://rpc-amoy.polygon.technology")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")


class BlockchainLogger:
    """Logs reconciliation decisions on-chain for tamper-proof audit trail."""

    def __init__(self):
        self.web3 = self._init_web3()
        self.local_log: List[Dict[str, Any]] = []

    def _init_web3(self):
        """Initialize Web3 connection."""
        try:
            from web3 import Web3
            if WEB3_PROVIDER_URL:
                w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
                if w3.is_connected():
                    return w3
        except (ImportError, Exception):
            pass
        return None

    def log_reconciliation(self, match_result: Dict[str, Any]) -> Dict[str, Any]:
        """Log a reconciliation decision on-chain."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "reconciliation",
            "invoice_ref": match_result.get("invoice", {}).get("reference", ""),
            "match_score": match_result.get("match_score", 0),
            "status": match_result.get("status", ""),
            "difference": match_result.get("difference", 0),
            "explanation": match_result.get("explanation", ""),
            "document_hash": self._hash_document(match_result),
        }

        # Try on-chain logging
        tx_hash = self._send_to_chain(log_entry)
        log_entry["tx_hash"] = tx_hash
        log_entry["on_chain"] = tx_hash is not None

        # Always keep local log
        self.local_log.append(log_entry)
        return log_entry

    def log_batch(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Log a batch of reconciliation results."""
        return [self.log_reconciliation(r) for r in results]

    def _send_to_chain(self, data: Dict[str, Any]) -> str:
        """Send data hash to Polygon testnet."""
        if not self.web3 or not WALLET_PRIVATE_KEY:
            return None

        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            data_hex = "0x" + data_str.encode().hex()

            nonce = self.web3.eth.get_transaction_count(WALLET_ADDRESS)
            tx = {
                "nonce": nonce,
                "to": WALLET_ADDRESS,  # Self-transaction with data
                "value": 0,
                "gas": 100000,
                "gasPrice": self.web3.to_wei("30", "gwei"),
                "data": data_hex,
                "chainId": 80002,  # Polygon Amoy testnet
            }

            signed = self.web3.eth.account.sign_transaction(tx, WALLET_PRIVATE_KEY)
            tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
            return self.web3.to_hex(tx_hash)
        except Exception:
            return None

    def _hash_document(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash of document for tamper detection."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get full audit trail."""
        return self.local_log

    def verify_integrity(self, entry: Dict[str, Any]) -> bool:
        """Verify an audit entry hasn't been tampered with."""
        stored_hash = entry.get("document_hash", "")
        # Reconstruct hash from original data
        original_data = {k: v for k, v in entry.items()
                       if k not in ["document_hash", "tx_hash", "on_chain", "timestamp", "type"]}
        computed_hash = self._hash_document(original_data)
        return stored_hash == computed_hash

    def export_audit_log(self) -> str:
        """Export audit log as JSON string."""
        return json.dumps(self.local_log, indent=2, default=str)
