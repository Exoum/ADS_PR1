"""Модуль музыкального плейера с графическим интерфейсом."""
import sys
import os
from typing import Dict, Optional
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
        QWidget, QPushButton, QListWidget, QInputDialog,
        QMessageBox, QLabel, QComboBox, QFileDialog,
        QGroupBox, QProgressBar, QTextEdit, QSplitter
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
except ImportError:
    # Заглушки для pylint
    QApplication = QMainWindow = QVBoxLayout = QHBoxLayout = None
    QWidget = QPushButton = QListWidget = QInputDialog = None
    QMessageBox = QLabel = QComboBox = QFileDialog = None
    QGroupBox = QProgressBar = QTextEdit = QSplitter = None
    Qt = QTimer = QFont = None
import pygame
from composition import Composition
from playlist import PlayList


class MusicPlayer(QMainWindow):
    """Музыкальный плейер с графическим интерфейсом."""

    def __init__(self) -> None:
        """Инициализация плейера."""
        super().__init__()
        self.playlists: Dict[str, PlayList] = {}
        self.current_playlist: Optional[PlayList] = None
        pygame.mixer.init()
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.init_ui()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("🎵 Музыкальный плейер")
        self.setGeometry(100, 100, 1200, 800)
        self._setup_styles()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной сплиттер
        main_splitter = QSplitter(Qt.Horizontal)

        # Левая панель - плейлисты и треки
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Группа плейлистов
        playlist_group = QGroupBox("🎧 Плейлисты")
        playlist_layout = QVBoxLayout(playlist_group)

        playlist_controls = QHBoxLayout()
        self.playlist_combo = QComboBox()
        self.playlist_combo.currentTextChanged.connect(self.select_playlist)

        create_playlist_btn = QPushButton("➕ Создать")
        create_playlist_btn.clicked.connect(self.create_playlist)

        delete_playlist_btn = QPushButton("❌ Удалить")
        delete_playlist_btn.clicked.connect(self.delete_playlist)

        playlist_controls.addWidget(self.playlist_combo)
        playlist_controls.addWidget(create_playlist_btn)
        playlist_controls.addWidget(delete_playlist_btn)
        playlist_layout.addLayout(playlist_controls)

        # Группа треков
        tracks_group = QGroupBox("🎵 Треки")
        tracks_layout = QVBoxLayout(tracks_group)

        self.track_list = QListWidget()
        self.track_list.setDragDropMode(QListWidget.InternalMove)
        self.track_list.itemChanged.connect(self.reorder_tracks)

        track_controls = QHBoxLayout()
        add_track_btn = QPushButton("🎵 Добавить")
        add_track_btn.clicked.connect(self.add_track)

        remove_track_btn = QPushButton("🗑️ Удалить")
        remove_track_btn.clicked.connect(self.remove_track)

        track_controls.addWidget(add_track_btn)
        track_controls.addWidget(remove_track_btn)

        tracks_layout.addWidget(self.track_list)
        tracks_layout.addLayout(track_controls)

        left_layout.addWidget(playlist_group)
        left_layout.addWidget(tracks_group)

        # Правая панель - плейер и информация
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Информация о треке
        info_group = QGroupBox("🎤 Информация о треке")
        info_layout = QVBoxLayout(info_group)

        self.track_info = QTextEdit()
        self.track_info.setMaximumHeight(150)
        self.track_info.setReadOnly(True)
        self.track_info.setStyleSheet("background-color: #3c3c3c; color: white; border: 1px solid #555;")
        info_layout.addWidget(self.track_info)

        # Плейер
        player_group = QGroupBox("🎶 Плейер")
        player_layout = QVBoxLayout(player_group)

        # Текущий трек
        self.current_track_label = QLabel("🎵 Не выбран")
        self.current_track_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.current_track_label.setAlignment(Qt.AlignCenter)

        # Прогресс бар
        progress_layout = QHBoxLayout()
        self.time_label = QLabel("00:00")
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #3c3c3c;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.duration_label = QLabel("00:00")

        progress_layout.addWidget(self.time_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.duration_label)

        # Кнопки управления
        control_layout = QHBoxLayout()
        prev_btn = QPushButton("⏮️ Предыдущий")
        prev_btn.clicked.connect(self.previous_track)

        self.play_btn = QPushButton("▶️ Играть")
        self.play_btn.clicked.connect(self.toggle_play)

        next_btn = QPushButton("⏭️ Следующий")
        next_btn.clicked.connect(self.next_track)

        # Увеличиваем размер кнопок
        for btn in [prev_btn, self.play_btn, next_btn]:
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 10))

        control_layout.addWidget(prev_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(next_btn)

        player_layout.addWidget(self.current_track_label)
        player_layout.addLayout(progress_layout)
        player_layout.addLayout(control_layout)

        # Статистика плейлиста
        stats_group = QGroupBox("📊 Статистика")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel("Количество треков: 0\nОбщая длительность: 00:00")
        stats_layout.addWidget(self.stats_label)

        right_layout.addWidget(info_group)
        right_layout.addWidget(player_group)
        right_layout.addWidget(stats_group)
        right_layout.addStretch()

        # Добавляем панели в сплиттер
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([600, 400])

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(main_splitter)

    def _setup_styles(self) -> None:
        """Настройка стилей интерфейса."""
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
                color: white;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton:hover { background-color: #5a5a5a; }
            QPushButton:pressed { background-color: #3a3a3a; }
            QLabel { color: white; }
            QComboBox {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 3px;
            }
        """)

    def create_playlist(self) -> None:
        """Создать новый плейлист."""
        name, ok = QInputDialog.getText(self, "Создать плейлист", "Название плейлиста:")
        if ok and name:
            if name not in self.playlists:
                self.playlists[name] = PlayList(name)
                self.playlist_combo.addItem(name)
                self.playlist_combo.setCurrentText(name)
                self.current_playlist = self.playlists[name]
                self.update_track_list()
            else:
                QMessageBox.warning(self, "Ошибка", "Плейлист с таким названием уже существует")

    def delete_playlist(self) -> None:
        """Удалить текущий плейлист."""
        current_name = self.playlist_combo.currentText()
        if current_name and current_name in self.playlists:
            reply = QMessageBox.question(
                self, "Удалить плейлист",
                f"Удалить плейлист '{current_name}'?"
            )
            if reply == QMessageBox.Yes:
                del self.playlists[current_name]
                current_index = self.playlist_combo.currentIndex()
                self.playlist_combo.removeItem(current_index)
                self.current_playlist = None
                self.update_track_list()

    def select_playlist(self, name: str) -> None:
        """Выбрать плейлист."""
        if name in self.playlists:
            self.current_playlist = self.playlists[name]
            self.update_track_list()
        else:
            self.current_playlist = None
            self.track_list.clear()

    def add_track(self) -> None:
        """Добавить трек в текущий плейлист."""
        if self.current_playlist is None:
            QMessageBox.warning(self, "Ошибка", "Выберите плейлист")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите аудиофайл", "",
            "Audio Files (*.mp3 *.wav *.ogg)"
        )

        if file_path:
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]

            artist, ok = QInputDialog.getText(
                self, "Добавить трек",
                "Исполнитель:", text="Unknown"
            )
            if ok:
                composition = Composition(title, artist, file_path=file_path)
                self.current_playlist.append(composition)
                self.update_track_list()

    def remove_track(self) -> None:
        """Удалить выбранный трек."""
        if not self.current_playlist:
            return

        current_row = self.track_list.currentRow()
        if current_row >= 0:
            track = self.current_playlist[current_row]
            self.current_playlist.remove(track)
            self.update_track_list()

    def update_track_list(self) -> None:
        """Обновить список треков."""
        self.track_list.clear()
        if self.current_playlist:
            for track in self.current_playlist:
                self.track_list.addItem(track.get_display_info())
        self.update_stats()

    def reorder_tracks(self) -> None:
        """Переупорядочить треки в плейлисте."""
        if not self.current_playlist:
            return

        new_order = []
        for i in range(self.track_list.count()):
            item_text = self.track_list.item(i).text()
            for track in self.current_playlist:
                if str(track) == item_text:
                    new_order.append(track)
                    break

        name = self.current_playlist.name
        self.current_playlist = PlayList(name)
        for track in new_order:
            self.current_playlist.append(track)
        self.playlists[name] = self.current_playlist

    def play_current(self) -> None:
        """Воспроизвести выбранный трек."""
        if not self.current_playlist or len(self.current_playlist) == 0:
            QMessageBox.warning(self, "Ошибка", "Плейлист пуст")
            return

        current_row = self.track_list.currentRow()
        if current_row >= 0:
            track = self.current_playlist[current_row]
        else:
            track = self.current_playlist[0]

        # Найти нужный трек и установить как текущий
        current = self.current_playlist.first_item
        for _ in range(len(self.current_playlist)):
            if current.track == track:
                self.current_playlist.current_item = current
                break
            current = current.next_item()
        self.current_track_label.setText(f"🎵 {track}")
        self.update_track_info(track)

        if track.file_path and os.path.exists(track.file_path):
            try:
                pygame.mixer.music.load(track.file_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.play_btn.setText("⏸️ Пауза")
                self.current_position = 0
                self.timer.start(1000)
            except Exception:  # pylint: disable=broad-except
                QMessageBox.warning(self, "Ошибка", "Не удалось воспроизвести файл")

    def next_track(self) -> None:
        """Перейти к следующему треку."""
        if self.current_playlist and self.current_playlist.current():
            next_track = self.current_playlist.next_track()
            if next_track:
                self.current_track_label.setText(f"🎵 {next_track}")
                self.update_track_info(next_track)
                if next_track.file_path and os.path.exists(next_track.file_path):
                    try:
                        pygame.mixer.music.load(next_track.file_path)
                        pygame.mixer.music.play()
                        self.current_position = 0
                        if not self.is_playing:
                            self.is_playing = True
                            self.play_btn.setText("⏸️ Пауза")
                            self.timer.start(1000)
                    except Exception:  # pylint: disable=broad-except
                        pass

    def previous_track(self) -> None:
        """Перейти к предыдущему треку."""
        if self.current_playlist and self.current_playlist.current():
            prev_track = self.current_playlist.previous_track()
            if prev_track:
                self.current_track_label.setText(f"🎵 {prev_track}")
                self.update_track_info(prev_track)
                if prev_track.file_path and os.path.exists(prev_track.file_path):
                    try:
                        pygame.mixer.music.load(prev_track.file_path)
                        pygame.mixer.music.play()
                        self.current_position = 0
                        if not self.is_playing:
                            self.is_playing = True
                            self.play_btn.setText("⏸️ Пауза")
                            self.timer.start(1000)
                    except Exception:  # pylint: disable=broad-except
                        pass

    def toggle_play(self) -> None:
        """Переключить воспроизведение/паузу."""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.play_btn.setText("▶️ Играть")
            self.is_playing = False
            self.is_paused = True
            self.timer.stop()
        else:
            if self.is_paused and self.current_playlist and self.current_playlist.current():
                current_track = self.current_playlist.current()
                self._resume_track(current_track)
            else:
                self.play_current()
                return
            self.play_btn.setText("⏸️ Пауза")
            self.is_playing = True
            self.timer.start(1000)

    def update_track_info(self, track: 'Composition') -> None:
        """Обновить информацию о треке."""
        file_name = (
            track.file_path.split('/')[-1].split('\\')[-1]
            if track.file_path else 'Нет файла'
        )
        path_info = track.file_path if track.file_path else 'Не указан'
        duration_min = track.duration // 60
        duration_sec = track.duration % 60

        info_text = (
            f"🎵 Название: {track.title}\n"
            f"🎤 Исполнитель: {track.artist}\n"
            f"⏱️ Длительность: {duration_min}:{duration_sec:02d} мин\n"
            f"📁 Файл: {file_name}\n"
            f"📍 Путь: {path_info}"
        )
        self.track_info.setText(info_text)

    def update_stats(self) -> None:
        """Обновить статистику плейлиста."""
        if self.current_playlist:
            track_count = len(self.current_playlist)
            total_duration = sum(track.duration for track in self.current_playlist)
            total_minutes = total_duration // 60
            total_seconds = total_duration % 60

            stats_text = (
                f"📊 Количество треков: {track_count}\n"
                f"⏱️ Общая длительность: {total_minutes}:{total_seconds:02d}\n"
                f"🎧 Плейлист: {self.current_playlist.name}"
            )
        else:
            stats_text = "📊 Плейлист не выбран"

        self.stats_label.setText(stats_text)

    def update_progress(self) -> None:
        """Обновить прогресс воспроизведения."""
        if self.is_playing and self.current_playlist and self.current_playlist.current():
            self.current_position += 1
            current_track = self.current_playlist.current()

            if current_track.duration > 0:
                progress = min(100, (self.current_position * 100) // current_track.duration)
                self.progress_bar.setValue(progress)

                # Обновляем время
                current_min = self.current_position // 60
                current_sec = self.current_position % 60
                self.time_label.setText(f"{current_min}:{current_sec:02d}")

                duration_min = current_track.duration // 60
                duration_sec = current_track.duration % 60
                self.duration_label.setText(f"{duration_min}:{duration_sec:02d}")

                # Автопереключение на следующий трек
                if self.current_position >= current_track.duration:
                    self.next_track()
                    self.current_position = 0

    def _resume_track(self, track) -> None:
        """Возобновить воспроизведение трека."""
        if track.file_path and os.path.exists(track.file_path):
            try:
                pygame.mixer.music.load(track.file_path)
                pygame.mixer.music.play(start=self.current_position)
                self.is_paused = False
            except Exception:  # pylint: disable=broad-except
                pass


def main() -> None:
    """Главная функция приложения."""
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
