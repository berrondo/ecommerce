class TestManager:
    def test_a_manager_is_created_in_the_correct_group(self, a_manager):
        assert a_manager.groups.first().name == 'managers'
        assert a_manager.is_manager()
