from abc import ABC, abstractmethod


class Interaction(ABC):
    """Abstract class: hanya mendefinisikan kontrak bahwa interaction harus punya interact()."""

    def __init__(self, actor, target):
        if actor is target or actor.user_id == target.user_id:
            raise ValueError("User tidak dapat berinteraksi dengan dirinya sendiri.")
        self._actor = actor  
        self._target = target

    @property
    def actor(self):
        return self._actor

    @property
    def target(self):
        return self._target

    @abstractmethod
    def interact(self):
        """Detail perilaku ditentukan oleh subclass."""


class Like(Interaction):
    def interact(self):
        return "LIKE"


class Pass(Interaction):
    def interact(self):
        return "PASS"


def process_interaction(interaction):
    """Menerima Like maupun Pass tanpa perlu tahu jenisnya; cukup memanggil interact()."""
    return interaction.interact()
