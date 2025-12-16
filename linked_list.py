"""Модуль для работы с кольцевым двусвязным списком."""
from typing import Any, Optional


class LinkedListItem:
    """Элемент связного списка."""

    def __init__(self, track) -> None:
        """Инициализация элемента."""
        self.track = track
        self._next: Optional['LinkedListItem'] = None
        self._previous: Optional['LinkedListItem'] = None

    def next_item(self) -> Optional['LinkedListItem']:
        """Получение следующего элемента."""
        return self._next

    def previous_item(self) -> Optional['LinkedListItem']:
        """Получение предыдущего элемента."""
        return self._previous


class LinkedList:
    """Кольцевой двусвязный список."""

    def __init__(self) -> None:
        """Инициализация списка."""
        self.first_item: Optional[LinkedListItem] = None
        self._tail: Optional[LinkedListItem] = None
        self._size = 0
        self._current: Optional[LinkedListItem] = None
        self._iter_count = 0



    def append_right(self, item) -> None:
        """Добавление элемента в конец списка."""
        new_item = LinkedListItem(item)

        if self._tail is None:
            self.first_item = self._tail = new_item
            new_item._next = new_item._previous = new_item
        else:
            new_item._previous = self._tail
            new_item._next = self.first_item
            self._tail._next = new_item
            self.first_item._previous = new_item
            self._tail = new_item
        self._size += 1

    def append(self, item) -> None:
        """Псевдоним для append_right."""
        self.append_right(item)

    def remove(self, item) -> None:
        """Удаление элемента из списка."""
        current = self.first_item
        if current is None:
            raise ValueError("Item not found")

        for _ in range(self._size):
            if current.track == item:
                if self._size == 1:
                    self.first_item = self._tail = None
                else:
                    current._previous._next = current._next
                    current._next._previous = current._previous
                    if current == self.first_item:
                        self.first_item = current._next
                    if current == self._tail:
                        self._tail = current._previous
                self._size -= 1
                return
            current = current._next
        raise ValueError("Item not found")



    def __len__(self) -> int:
        """Возврат количества элементов в списке."""
        return self._size

    def __iter__(self) -> 'LinkedList':
        """Инициализация итератора для обхода списка."""
        self._current = self.first_item
        self._iter_count = 0
        return self

    def __next__(self) -> Any:
        """Получение следующего элемента при итерации."""
        if self._current is None or self._iter_count >= self._size:
            raise StopIteration
        data = self._current.track
        self._current = self._current._next
        self._iter_count += 1
        return data

    def __getitem__(self, index: int) -> Any:
        """Получение элемента по индексу."""
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        current = self.first_item
        for _ in range(index):
            current = current._next
        return current.track

    def __contains__(self, item) -> bool:
        """Проверка наличия элемента в списке."""
        current = self.first_item
        for _ in range(self._size):
            if current.track == item:
                return True
            current = current._next
        return False


