"""Модуль для работы с плейлистом."""

from linked_list import LinkedList



class PlayList(LinkedList):
    """Плейлист на основе кольцевого списка."""

    def __init__(self, name: str) -> None:
        """Инициализация плейлиста.

        Args:
            name: Название плейлиста
        """
        super().__init__()
        self.name = name
        self.current_item = None



    def next_track(self):
        """Перейти к следующему треку."""
        if self.current_item and self._size > 0:
            self.current_item = self.current_item.next_item()
            return self.current_item.track
        return None

    def previous_track(self):
        """Перейти к предыдущему треку."""
        if self.current_item and self._size > 0:
            self.current_item = self.current_item.previous_item()
            return self.current_item.track
        return None

    def current(self):
        """Получить текущую композицию."""
        if self.current_item:
            return self.current_item.track
        return None


