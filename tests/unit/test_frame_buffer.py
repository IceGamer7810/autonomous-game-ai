from game_agent.game_adapter import FrameBuffer


def test_frame_buffer_overwrites_oldest_frame():
    buffer = FrameBuffer[str](capacity=2)
    buffer.append("first", 1)
    buffer.append("second", 2)
    buffer.append("third", 3)

    assert [frame.payload for frame in buffer.snapshot()] == ["second", "third"]
    assert buffer.latest().payload == "third"
    assert buffer.dropped_frames == 1
    assert buffer.occupancy == 2
