"""Тесты для музыкального плейера."""
import unittest
from composition import Composition
from playlist import PlayList
from linked_list import LinkedList


class TestComposition(unittest.TestCase):
    """Тесты для класса Composition."""

    def test_composition_creation(self) -> None:
        """Тест создания композиции."""
        comp = Composition("Test Song", "Test Artist", 180)
        self.assertEqual(comp.title, "Test Song")
        self.assertEqual(comp.artist, "Test Artist")
        self.assertEqual(comp.duration, 180)

    def test_composition_str(self) -> None:
        """Тест строкового представления."""
        comp = Composition("Test Song", "Test Artist")
        self.assertEqual(str(comp), "Test Artist - Test Song")

    def test_composition_equality(self) -> None:
        """Тест сравнения композиций."""
        comp1 = Composition("Song", "Artist")
        comp2 = Composition("Song", "Artist")
        comp3 = Composition("Other", "Artist")

        self.assertEqual(comp1, comp2)
        self.assertNotEqual(comp1, comp3)


class TestLinkedList(unittest.TestCase):
    """Тесты для класса LinkedList."""

    def setUp(self) -> None:
        """Подготовка к тестам."""
        self.linked_list = LinkedList()

    def test_append_and_len(self) -> None:
        """Тест добавления элементов и подсчета длины."""
        self.linked_list.append("item1")
        self.linked_list.append("item2")
        self.assertEqual(len(self.linked_list), 2)

    def test_contains(self) -> None:
        """Тест проверки наличия элемента."""
        self.linked_list.append("item1")
        self.assertIn("item1", self.linked_list)
        self.assertNotIn("item2", self.linked_list)

    def test_remove(self) -> None:
        """Тест удаления элемента."""
        self.linked_list.append("item1")
        self.linked_list.append("item2")
        self.linked_list.remove("item1")
        self.assertEqual(len(self.linked_list), 1)
        self.assertNotIn("item1", self.linked_list)

    def test_getitem(self) -> None:
        """Тест получения элемента по индексу."""
        self.linked_list.append("item1")
        self.linked_list.append("item2")
        self.assertEqual(self.linked_list[0], "item1")
        self.assertEqual(self.linked_list[1], "item2")


class TestPlayList(unittest.TestCase):
    """Тесты для класса PlayList."""

    def setUp(self) -> None:
        """Подготовка к тестам."""
        self.playlist = PlayList("Test Playlist")
        self.comp1 = Composition("Song1", "Artist1")
        self.comp2 = Composition("Song2", "Artist2")

    def test_playlist_creation(self) -> None:
        """Тест создания плейлиста."""
        self.assertEqual(self.playlist.name, "Test Playlist")
        self.assertEqual(len(self.playlist), 0)

    def test_add_tracks(self) -> None:
        """Тест добавления треков."""
        self.playlist.append(self.comp1)
        self.playlist.append(self.comp2)
        self.assertEqual(len(self.playlist), 2)

    def test_play_all(self) -> None:
        """Тест начала воспроизведения."""
        self.playlist.append(self.comp1)
        self.playlist.append(self.comp2)
        self.playlist.play_all()
        self.assertEqual(self.playlist.current(), self.comp1)

    def test_next_previous_track(self) -> None:
        """Тест переключения треков."""
        self.playlist.append(self.comp1)
        self.playlist.append(self.comp2)
        self.playlist.play_all()

        next_track = self.playlist.next_track()
        self.assertEqual(next_track, self.comp2)

        prev_track = self.playlist.previous_track()
        self.assertEqual(prev_track, self.comp1)


if __name__ == "__main__":
    unittest.main()
