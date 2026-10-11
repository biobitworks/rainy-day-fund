"""Storage adapters. MongoStore is the only Atlas-backed one; MemoryStore/FileStore are
LOCAL test doubles and every receipt must label them as such (never as Atlas evidence)."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any

PROJECT_ID = "RDF-SFTW26-NEW-001"
OFFICIAL_ATLAS_PROJECT = "6acba49b5c102b1d2b95a0ac"
DB_NAME = "rainy_day_fund_sftw26"
TICKETS, EVENTS, WEBHOOKS, PARKED = ("integration_smoke_tickets", "integration_smoke_events",
                                    "integration_smoke_webhooks", "integration_smoke_parked")
FIXTURES = "ticket_fixtures"  # frozen, read-only
LIVE_TICKETS, LIVE_EVENTS, LIVE_WEBHOOKS, LIVE_IDEM = ("live_tickets", "live_events", "live_webhooks", "live_idempotency")


class StoreError(Exception):
    """Storage unavailable/failed; callers must report FAILED, never success."""


class MemoryStore:
    kind = "LOCAL_MEMORY_NOT_ATLAS"

    def __init__(self, fixtures: list[dict] | None = None):
        self.data: dict[str, dict[str, dict]] = {FIXTURES: {f["_id"]: dict(f) for f in (fixtures or [])}}

    def _c(self, coll):
        return self.data.setdefault(coll, {})

    def get(self, coll: str, _id: str) -> dict | None:
        d = self._c(coll).get(_id)
        return json.loads(json.dumps(d)) if d is not None else None

    def insert_if_absent(self, coll: str, doc: dict) -> bool:
        """$setOnInsert semantics. True if inserted, False if it already existed."""
        c = self._c(coll)
        if doc["_id"] in c:
            return False
        c[doc["_id"]] = json.loads(json.dumps(doc))
        return True

    def update(self, coll: str, _id: str, fields: dict) -> None:
        self._c(coll)[_id].update(fields)

    def list(self, coll: str, limit: int = 200, sort_key: str = "created_at") -> list[dict]:
        rows = [json.loads(json.dumps(d)) for d in self._c(coll).values()]
        return sorted(rows, key=lambda d: d.get(sort_key) or "", reverse=True)[:limit]

    def count(self, coll: str, flt: dict | None = None) -> int:
        return sum(all(d.get(k) == v for k, v in (flt or {}).items()) for d in self._c(coll).values())


class FileStore(MemoryStore):
    """Durable local JSON file so a *fresh process* can read prior state (restart test)."""
    kind = "LOCAL_FILE_NOT_ATLAS"

    def __init__(self, path: Path, fixtures: list[dict] | None = None):
        self.path = Path(path)
        super().__init__(fixtures)
        if self.path.exists():
            self.data = json.loads(self.path.read_text())

    def _flush(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, sort_keys=True))
        os.replace(tmp, self.path)

    def insert_if_absent(self, coll, doc):
        r = super().insert_if_absent(coll, doc); self._flush(); return r

    def update(self, coll, _id, fields):
        super().update(coll, _id, fields); self._flush()


class FaultyStore:
    """Wrap a store and fail on demand (failed-Atlas-write negative test)."""
    def __init__(self, inner, fail_writes=False, fail_reads=False):
        self.inner, self.fail_writes, self.fail_reads = inner, fail_writes, fail_reads
        self.kind = "FAULT_INJECTED(" + inner.kind + ")"

    def get(self, *a):
        if self.fail_reads: raise StoreError("injected read failure")
        return self.inner.get(*a)

    def insert_if_absent(self, *a):
        if self.fail_writes: raise StoreError("injected write failure")
        return self.inner.insert_if_absent(*a)

    def update(self, *a):
        if self.fail_writes: raise StoreError("injected write failure")
        return self.inner.update(*a)

    def count(self, *a):
        return self.inner.count(*a)

    def list(self, *a, **k):
        if self.fail_reads: raise StoreError("injected read failure")
        return self.inner.list(*a, **k)


class MongoStore:
    """Atlas adapter. Fails closed: requires a credentialled URI, exact db name, never logs the URI."""
    kind = "ATLAS"

    def __init__(self, uri: str, db: str = DB_NAME, timeout_ms: int = 8000):
        from urllib.parse import urlsplit
        if db != DB_NAME:
            raise StoreError("database must be " + DB_NAME)
        u = urlsplit(uri)
        if not (u.username and u.password):
            raise StoreError("MONGODB_URI lacks username/password (fail closed)")
        from pymongo import MongoClient, WriteConcern
        self._wc = WriteConcern(w="majority")
        self.db = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)[db]
        self.host = u.hostname

    def _wrap(self, fn):
        try:
            return fn()
        except Exception as e:  # sanitize: class name only
            raise StoreError(type(e).__name__) from None

    def get(self, coll, _id):
        return self._wrap(lambda: self.db[coll].find_one({"_id": _id, "project_id": PROJECT_ID}))

    def insert_if_absent(self, coll, doc):
        def go():
            r = self.db.get_collection(coll, write_concern=self._wc).update_one(
                {"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)
            return r.upserted_id is not None
        return self._wrap(go)

    def update(self, coll, _id, fields):
        self._wrap(lambda: self.db.get_collection(coll, write_concern=self._wc).update_one(
            {"_id": _id, "project_id": PROJECT_ID}, {"$set": fields}))

    def count(self, coll, flt=None):
        return self._wrap(lambda: self.db[coll].count_documents({"project_id": PROJECT_ID, **(flt or {})}))

    def list(self, coll, limit=200, sort_key="created_at"):
        return self._wrap(lambda: list(self.db[coll].find({"project_id": PROJECT_ID}).sort(sort_key, -1).limit(limit)))

class UnconfiguredStore:
    """Used when no credentialled Atlas URI exists: every operation fails closed (never reports success)."""
    kind = "UNCONFIGURED_FAIL_CLOSED"
    def _no(self, *a, **k):
        raise StoreError("store unconfigured: credentialled MONGODB_URI missing")
    get = insert_if_absent = update = count = list = _no
