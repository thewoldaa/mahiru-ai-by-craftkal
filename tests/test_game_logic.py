from story_engine.relationship_system import RelationshipSystem


def test_relationship_level():
    system = RelationshipSystem()
    assert system.get_level(85) == 'Love'
