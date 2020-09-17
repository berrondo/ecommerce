from ..models import User


class TestManager:
    def test_a_manager_is_created_in_the_correct_group(self, a_manager):
        assert User.objects.exists()
        assert a_manager.groups.first().name == 'managers'
