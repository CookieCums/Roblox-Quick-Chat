from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QScrollArea, \
    QGridLayout, QSizePolicy, QFrame, QLabel, QHBoxLayout, QMessageBox, QFileDialog, QSpacerItem
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QPainterPath, QRegion
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRectF

import sys
import time
import ctypes
import keyboard
import pyperclip
import webbrowser

SW_RESTORE = 9

class MessageSenderThread(QThread):
    messageSent = pyqtSignal(str)

    def run(self):
        self.focus_on_app('Roblox')
        try:
            pyperclip.copy(self.message.strip())
            keyboard.press_and_release('/')
            time.sleep(0.03)
            keyboard.press_and_release('ctrl+v')
            time.sleep(0.04)
            keyboard.press_and_release('Enter')
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def focus_on_app(self, app_title):
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, app_title)
        if hwnd:
            user32.SetForegroundWindow(hwnd)
        else:
            print(f"Error: Could not find the window with title '{app_title}'")

    def __del__(self):
        self.wait()

class CustomTitleBar(QWidget):
    customTextFileSelected = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.create_label("Roblox Quick Chat"), 1, Qt.AlignCenter)
        layout.addLayout(self.create_button_layout(parent))

        self.enable_dragging(True)

    def create_label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 12pt; font-weight: bold;")
        return label

    def create_button_layout(self, parent):
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        buttons = [
            ("❓", self.show_donate_message),
            ("-", parent.showMinimized),
            ("🗀", self.select_custom_text_file),
            ("×", parent.close)
        ]
        for text, func in buttons:
            button_layout.addWidget(self.create_button(text, func))
        return button_layout

    def create_button(self, text, function):
        button = QPushButton(text)
        button.clicked.connect(function)
        self.apply_button_style(button)
        button.setFixedSize(20, 20)
        return button

    def select_custom_text_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Custom Text File", "", "Text Files (*.txt)")
        if file_name:
            self.customTextFileSelected.emit(file_name)

    def show_donate_message(self):
        self.show_message_box('Support Us', 'Would you like to support our project?', 'https://linktr.ee/spookiepooki')

    def show_message_box(self, title, text, url=None):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStyleSheet(self.message_box_stylesheet())
        box.addButton(QMessageBox.Yes)
        box.addButton(QMessageBox.No)
        if box.exec_() == QMessageBox.Yes and url:
            pyperclip.copy(url)
            self.show_message_box('URL Copied', f'The donation URL has been copied to the clipboard:\n\n{url}')
            webbrowser.open(url)

    def message_box_stylesheet(self):
        return """
            QMessageBox { background-color: #2E2E2E; border: 2px solid #393939; border-radius: 10px; }
            QMessageBox QLabel { color: #FFFFFF; }
            QMessageBox QPushButton { background-color: #555555; color: white; border: none; padding: 5px; border-radius: 5px; }
            QMessageBox QPushButton:hover { background-color: #666666; }
        """

    def enable_dragging(self, enable=True):
        if enable:
            self.mousePressEvent = self.mousePress
            self.mouseMoveEvent = self.mouseMove
        else:
            self.mousePressEvent = None
            self.mouseMoveEvent = None

    def mousePress(self, event):
        self.offset = event.pos()

    def mouseMove(self, event):
        if hasattr(self, 'offset'):
            self.parent().move(event.globalX() - self.offset.x(), event.globalY() - self.offset.y())

    def apply_button_style(self, button):
        button.setStyleSheet("""
            QPushButton { border: none; color: white; font-size: 14px; font-weight: bold; background-color: #555555; border-radius: 5px; padding: 2px; }
            QPushButton:hover { background-color: #666666; }
        """)

class RoundedWindow(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roblox Quick Chat")
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(300, 200)
        self.set_background_image("resources/Background_Image.webp")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        title_bar = CustomTitleBar(self)
        title_bar.customTextFileSelected.connect(self.load_custom_text_file)
        layout.addWidget(title_bar)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        layout.addWidget(self.scroll_area)

        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 10, 0)
        self.content_layout.setSpacing(5)
        self.load_default_messages()

        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)

        self.set_rounded_edges()
        layout.setAlignment(Qt.AlignTop)
        self.enable_dragging(True)
        self.show()

    def load_custom_text_file(self, file_path):
        self.clear_layout(self.content_layout)
        self.load_messages(file_path)

    def load_default_messages(self):
        self.load_messages('resources/messages.txt')

    def load_messages(self, file_path):
        with open(file_path, 'r') as file:
            messages = [line.strip() for line in file.readlines()]

        for i, message in enumerate(messages):
            button = QPushButton(message)
            self.apply_button_style(button)
            button.clicked.connect(lambda _, m=message: self.on_message_click(m))
            self.content_layout.addWidget(button, i // 3, i % 3)

        # Add a spacer item to ensure proper layout
        self.content_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), (len(messages) + 2) // 3, 0, 1, 3)

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    layout.removeWidget(widget)
                    widget.setParent(None)

    def on_message_click(self, message):
        message_sender_thread = MessageSenderThread()
        message_sender_thread.message = message
        message_sender_thread.start()

    def set_rounded_edges(self):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def enable_dragging(self, enable=True):
        if enable:
            self.mousePressEvent = self.mousePress
            self.mouseMoveEvent = self.mouseMove
        else:
            self.mousePressEvent = None
            self.mouseMoveEvent = None

    def mousePress(self, event):
        self.offset = event.pos()

    def mouseMove(self, event):
        if hasattr(self, 'offset'):
            self.move(event.globalX() - self.offset.x(), event.globalY() - self.offset.y())

    def apply_button_style(self, button):
        full_message = button.text()
        button.setStyleSheet("""
            QPushButton { border: none; padding: 10px 5px; font-size: 10pt; background-color: #555555; color: black; border-radius: 5px; max-width: 100px; }
        """)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setText(self.truncate_text(full_message, 11))
        button.setToolTip(full_message)

    def truncate_text(self, text, max_length):
        return text if len(text) <= max_length else text[:max_length - 3] + "..."

    def set_background_image(self, image_path):
        palette = QPalette()
        background_image = QPixmap(image_path).scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        palette.setBrush(QPalette.Window, QBrush(background_image))
        self.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoundedWindow()
    sys.exit(app.exec_())
