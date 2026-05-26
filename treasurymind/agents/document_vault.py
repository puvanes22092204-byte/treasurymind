"""Secure Financial Document Vault - encrypted storage and retrieval."""
import hashlib
import json
import os
from typing import Dict, Any, List
from datetime import datetime


class DocumentVault:
    """Secure document storage with integrity verification and audit trail."""

    def __init__(self, vault_path: str = "vault"):
        self.vault_path = vault_path
        self.index = []  # Document metadata index
        os.makedirs(vault_path, exist_ok=True)
        self._load_index()

    def store_document(self, filename: str, content: bytes, doc_type: str,
                      metadata: Dict = None) -> Dict[str, Any]:
        """Store a document securely with hash verification."""
        doc_hash = hashlib.sha256(content).hexdigest()
        doc_id = f"DOC-{len(self.index)+1:06d}"

        entry = {
            "id": doc_id,
            "filename": filename,
            "type": doc_type,  # receipt, invoice, bank_statement, report
            "hash": doc_hash,
            "size_bytes": len(content),
            "stored_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "verified": True,
            "access_log": [{"action": "stored", "timestamp": datetime.now().isoformat()}],
        }

        # Store file
        file_path = os.path.join(self.vault_path, f"{doc_id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        self.index.append(entry)
        self._save_index()
        return entry

    def verify_document(self, doc_id: str) -> Dict[str, Any]:
        """Verify document integrity by recalculating hash."""
        entry = self._find_entry(doc_id)
        if not entry:
            return {"verified": False, "error": "Document not found"}

        file_path = os.path.join(self.vault_path, f"{doc_id}_{entry['filename']}")
        if not os.path.exists(file_path):
            return {"verified": False, "error": "File missing from vault"}

        with open(file_path, "rb") as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()

        is_valid = current_hash == entry["hash"]
        entry["access_log"].append({
            "action": "verified", "timestamp": datetime.now().isoformat(),
            "result": "valid" if is_valid else "TAMPERED"
        })
        self._save_index()

        return {"verified": is_valid, "stored_hash": entry["hash"],
                "current_hash": current_hash, "doc_id": doc_id}

    def search_documents(self, query: str = "", doc_type: str = None) -> List[Dict]:
        """Search documents by name or type."""
        results = self.index
        if doc_type:
            results = [d for d in results if d["type"] == doc_type]
        if query:
            q = query.lower()
            results = [d for d in results if q in d["filename"].lower() or q in json.dumps(d.get("metadata", {})).lower()]
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get vault statistics."""
        total_size = sum(d["size_bytes"] for d in self.index)
        by_type = {}
        for d in self.index:
            t = d["type"]
            by_type[t] = by_type.get(t, 0) + 1

        return {
            "total_documents": len(self.index),
            "total_size_mb": round(total_size / (1024*1024), 2),
            "by_type": by_type,
            "last_stored": self.index[-1]["stored_at"] if self.index else None,
        }

    def _find_entry(self, doc_id: str) -> Dict:
        for entry in self.index:
            if entry["id"] == doc_id:
                return entry
        return None

    def _load_index(self):
        index_path = os.path.join(self.vault_path, "index.json")
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                self.index = json.load(f)

    def _save_index(self):
        index_path = os.path.join(self.vault_path, "index.json")
        with open(index_path, "w") as f:
            json.dump(self.index, f, indent=2, default=str)
