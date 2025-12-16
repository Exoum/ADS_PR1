"""Модуль для работы с музыкальными композициями."""
from typing import Any
import os
try:
    from mutagen.mp3 import MP3  # type: ignore
    from mutagen.wave import WAVE  # type: ignore
    from mutagen.oggvorbis import OggVorbis  # type: ignore
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


class Composition:
    """Класс для представления музыкальной композиции."""

    def __init__(self, title: str, artist: str, duration: int = 0,
                 file_path: str = "") -> None:
        """Инициализация композиции.

        Args:
            title: Название композиции
            artist: Исполнитель
            duration: Длительность в секундах
            file_path: Путь к аудиофайлу
        """
        self.title = title
        self.artist = artist
        self.file_path = file_path
        if duration > 0:
            self.duration = duration
        else:
            self.duration = self._get_duration_from_file()

    def _get_duration_from_file(self) -> int:
        """Получить длительность из аудиофайла."""
        # Проверка наличия пути к файлу и его существования
        if not self.file_path or not os.path.exists(self.file_path):
            return 0

        # Проверка доступности библиотеки mutagen для чтения метаданных
        if not MUTAGEN_AVAILABLE:
            return 0

        try:
            # Определение типа аудиофайла по расширению
            if self.file_path.lower().endswith('.mp3'):
                audio = MP3(self.file_path)
            elif self.file_path.lower().endswith('.wav'):
                audio = WAVE(self.file_path)
            elif self.file_path.lower().endswith('.ogg'):
                audio = OggVorbis(self.file_path)
            else:
                # Неподдерживаемый формат файла
                return 0

            # Извлечение длительности из метаданных
            if audio.info.length:
                return int(audio.info.length)
            return 0
        except (OSError, IOError):
            # Обработка любых ошибок при чтении файла
            return 0

    def __str__(self) -> str:
        """Строковое представление композиции."""
        if self.duration > 0:
            duration_str = f" ({self.duration}s)"
        else:
            duration_str = ""
        return f"{self.artist} - {self.title}{duration_str}"

    def get_display_info(self) -> str:
        """Полная информация для отображения."""
        # Форматирование длительности
        if self.duration > 0:
            minutes = self.duration // 60
            seconds = self.duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "--:--"

        # Извлечение имени файла
        if self.file_path:
            file_name = self.file_path.split('/')[-1].split('\\')[-1]
        else:
            file_name = "Нет файла"

        return f"{self.artist} - {self.title} [{duration_str}] ({file_name})"

    def __eq__(self, other: Any) -> bool:
        """Сравнение композиций на равенство."""
        if not isinstance(other, Composition):
            return False
        return self.title == other.title and self.artist == other.artist
