import os
import stat
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from make_it_rain.config import load_env, database_uri


def test_masked_env_status_and_alias(tmp_path, monkeypatch):
    for key in ("MONGODB_URI","ATLAS_MONGODB_URI","ELEVENLABS_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    p=tmp_path/".env"
    p.write_text("MONGODB_URI=FAKE_UNIT_TEST_URI\nELEVENLABS_API_KEY=FAKE_UNIT_TEST_KEY\nELEVENLABS_AGENT_ID=\n")
    p.chmod(0o600)
    status=load_env(tmp_path)
    assert status["MONGODB_URI"]=="SET"
    assert status["ELEVENLABS_AGENT_ID"]=="EMPTY"
    assert status["ELEVENLABS_API_KEY"]=="SET"
    assert "FAKE_UNIT_TEST_KEY" not in str(status)
    assert database_uri()=="FAKE_UNIT_TEST_URI"


def test_world_readable_env_rejected(tmp_path, monkeypatch):
    p=tmp_path/".env"
    p.write_text("MONGODB_URI=FAKE_UNIT_TEST_URI\n")
    p.chmod(0o644)
    if os.name=="posix":
        try:
            load_env(tmp_path)
        except PermissionError as e:
            assert "FAKE_UNIT_TEST_URI" not in str(e)
        else:
            raise AssertionError("must block world-readable environment")
