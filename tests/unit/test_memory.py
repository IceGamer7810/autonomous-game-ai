from game_agent.memory import MemoryStore


def test_memory_store_uses_fts_for_compact_observations(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    store.create_session("s", "goal", "window", "now")
    store.add_observation("s", "hash", "visible menu prompt", 0.9, "now")

    matches = store.search_observations("menu")
    assert len(matches) == 1
    assert matches[0]["frame_hash"] == "hash"
    store.close()
