from pathlib import Path

from story_engine.story_loader import StoryLoader


def test_get_scene():
    loader = StoryLoader(Path('story_data'))
    scene = loader.get_scene('ch1_scene_1')
    assert scene is not None
    assert scene['chapter'] == 1
