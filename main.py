import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings
from yt_dlp import YoutubeDL

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings('MyApp', 'YouTubeDownloader')
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle('YoinkTube - YouTube Downloader')
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #323232;
                color: #FFFFFF;
                border: none;
            }
            QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox {
                border-radius: 10px;
                padding: 6px;
                margin: 2px;
            }
            QPushButton {
                background-color: #5F5F5F;
                color: #FFFFFF;
                padding: 10px;
                border-color: #686868;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QLineEdit, QComboBox {
                background-color: #424242;
                color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/downarrow-16.png);
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid darkgray;
                selection-background-color: #6e6e6e;
                padding: 10px;
                border-radius: 5px;
                background-color: #323232;
                color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout()

        self.url_label = QLabel('URL:', self)
        self.url_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.url_label)
        
        self.url_entry = QLineEdit(self)
        layout.addWidget(self.url_entry)

        self.output_dir_label = QLabel('Output Directory:', self)
        self.output_dir_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.output_dir_label)

        self.output_dir_entry = QLineEdit(self)
        self.output_dir_entry.setReadOnly(True)
        layout.addWidget(self.output_dir_entry)

        self.choose_dir_button = QPushButton('Choose Directory', self)
        self.choose_dir_button.clicked.connect(self.choose_output_dir)
        layout.addWidget(self.choose_dir_button)

        self.audio_only_checkbox = QCheckBox('Download Audio Only (MP3)', self)
        layout.addWidget(self.audio_only_checkbox)

        self.audio_bitrate_label = QLabel('Audio Bitrate (kbps):', self)
        self.audio_bitrate_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.audio_bitrate_label)

        self.audio_bitrate_combobox = QComboBox(self)
        self.audio_bitrate_combobox.addItems(['Highest Quality', '64', '128', '192', '256', '320'])
        layout.addWidget(self.audio_bitrate_combobox)

        self.format_label = QLabel('Format:', self)
        self.format_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.format_label)

        self.format_combobox = QComboBox(self)
        self.format_combobox.addItems(['mp4', 'webm'])
        layout.addWidget(self.format_combobox)

        self.quality_label = QLabel('Video Quality:', self)
        self.quality_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.quality_label)

        self.quality_combobox = QComboBox(self)
        self.quality_combobox.addItems(['Highest Quality', '480p', '720p', '1080p'])
        layout.addWidget(self.quality_combobox)

        self.download_button = QPushButton('Download', self)
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def choose_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if output_dir:
            self.output_dir_entry.setText(output_dir)

    def download_video(self):
        url = self.url_entry.text()
        output_dir = self.output_dir_entry.text()
        format_option = self.format_combobox.currentText()
        quality_option = self.quality_combobox.currentText()
        audio_bitrate_option = self.audio_bitrate_combobox.currentText()
        audio_only = self.audio_only_checkbox.isChecked()

        if not url or not output_dir:
            QMessageBox.warning(self, 'Warning', 'URL and Output Directory are required')
            return

        if audio_only:
            preferred_bitrate = 'bestaudio/best' if audio_bitrate_option == 'Highest Quality' else f'bestaudio[abr<={audio_bitrate_option}]'
            ydl_opts = {
                'format': preferred_bitrate,
                'outtmpl': output_dir + '/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_bitrate_option if audio_bitrate_option != 'Highest Quality' else '320',
                }]
            }
        else:
            video_quality = {
                'Highest Quality': 'bestvideo+bestaudio/best',
                '480p': 'bestvideo[height<=480]+bestaudio/best',
                '720p': 'bestvideo[height<=720]+bestaudio/best',
                '1080p': 'bestvideo[height<=1080]+bestaudio/best'
            }.get(quality_option, 'bestvideo+bestaudio/best')

            ydl_opts = {
                'format': video_quality.replace('bestaudio/best', f'bestaudio[ext=m4a]/best').replace('bestvideo', f'bestvideo[ext={format_option}]'),
                'outtmpl': output_dir + '/%(title)s.%(ext)s',
            }

        try:
            ydl = YoutubeDL(ydl_opts)
            ydl.download([url])
            QMessageBox.information(self, 'Success', 'Download Completed Successfully')
            self.save_settings()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def save_settings(self):
        self.settings.setValue('output_dir', self.output_dir_entry.text())
        self.settings.setValue('format', self.format_combobox.currentText())
        self.settings.setValue('quality', self.quality_combobox.currentText())
        self.settings.setValue('audio_bitrate', self.audio_bitrate_combobox.currentText())
        self.settings.setValue('audio_only', self.audio_only_checkbox.isChecked())

    def load_settings(self):
        output_dir = self.settings.value('output_dir', '')
        format_option = self.settings.value('format', 'mp4')
        quality_option = self.settings.value('quality', 'Highest Quality')
        audio_bitrate_option = self.settings.value('audio_bitrate', 'Highest Quality')
        audio_only = self.settings.value('audio_only', 'false') == 'true'

        self.output_dir_entry.setText(output_dir)
        self.format_combobox.setCurrentText(format_option)
        self.quality_combobox.setCurrentText(quality_option)
        self.audio_bitrate_combobox.setCurrentText(audio_bitrate_option)
        self.audio_only_checkbox.setChecked(audio_only)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec())
