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
import ctypes
user32 = ctypes.windll.user32
SW_RESTORE = 9

class WorkerThread(QThread):
    messageClicked = pyqtSignal(str)

    def run(self):
        app_title_to_focus = 'Roblox'
        self.focus_on_app(app_title_to_focus)

        try:
            user32.keybd_event(0xBF, 0, 0, 0); user32.keybd_event(0xBF, 0, 2, 0)
            time.sleep(0.04)
            pyperclip.copy(self.message.strip())
            user32.keybd_event(0x11, 0, 0, 0); user32.keybd_event(0x56, 0, 0, 0); user32.keybd_event(0x56, 0, 2, 0); user32.keybd_event(0x11, 0, 2, 0)

            time.sleep(0.05)
            keyboard.press_and_release('Enter')

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def focus_on_app(self, app_title):
        user32 = ctypes.windll.user32
        SetForegroundWindow = user32.SetForegroundWindow
        FindWindow = user32.FindWindowW

        try:
            hwnd = FindWindow(None, app_title)

            if hwnd == 0:
                print(f"Error: Could not find the window with title '{app_title}'")
                return

            SetForegroundWindow(hwnd)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def __del__(self):
        self.wait()


class TitleBar(QWidget):
    customTextFileSelected = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)


        title_label = QLabel("Roblox Quick Chat")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 12pt; font-weight: bold;")
        layout.addWidget(title_label, 1, Qt.AlignCenter)


        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        minimize_button = self.setup_minimize_button()
        button_layout.addWidget(minimize_button)

        minimize_button = QPushButton("-")
        minimize_button.clicked.connect(parent.showMinimized)
        self.apply_button_style(minimize_button)
        minimize_button.setFixedSize(18, 18)
        button_layout.addWidget(minimize_button)

        custom_text_button = QPushButton("...")
        custom_text_button.clicked.connect(self.select_custom_text_file)
        self.apply_button_style(custom_text_button)
        custom_text_button.setFixedSize(20, 20)
        button_layout.addWidget(custom_text_button)

        close_button = QPushButton("×")
        close_button.clicked.connect(parent.close)
        self.apply_button_style(close_button)
        close_button.setFixedSize(20, 20)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.draggable(True)

    def select_custom_text_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Custom Text File", "", "Text Files (*.txt)", options=options)
        if file_name:
            self.customTextFileSelected.emit(file_name)

    def setup_minimize_button(self):
        minimize_button = QPushButton("❓")
        minimize_button.clicked.connect(self.minimize_button_clicked)
        self.apply_button_style(minimize_button)
        minimize_button.setFixedSize(20, 20)
        minimize_button.setStyleSheet("background-color: transparent; text-align: center;")
        return minimize_button

    def minimize_button_clicked(self):
        message_box_stylesheet = """
            QMessageBox {
                background-color: #2E2E2E;
                border: 2px solid #393939;
                border-radius: 99px;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
            }
        """

        reply_box = QMessageBox(self)
        reply_box.setWindowTitle('Donate And Social')
        reply_box.setText('Would you like to support?')

        reply_box.setStyleSheet(message_box_stylesheet)

        reply_box.addButton(QMessageBox.Yes)
        reply_box.addButton(QMessageBox.No)

        reply = reply_box.exec_()

        if reply == QMessageBox.Yes:
            time.sleep(1)
            donation_url = 'https://linktr.ee/spookiepooki'
            pyperclip.copy(donation_url)

            copy_message_box = QMessageBox(self)
            copy_message_box.setWindowTitle('URL Copied')
            copy_message_box.setText(
                f'The donation URL has been copied to the clipboard press ok to open it:\n\n{donation_url}')

            copy_message_box.setStyleSheet(message_box_stylesheet)

            copy_message_box.addButton(QMessageBox.Ok)
            copy_message_box.addButton(QMessageBox.No)

            response = copy_message_box.exec_()

            if response == QMessageBox.Ok:
                webbrowser.open(donation_url)
            else:

                thanks_box = QMessageBox(self)
                thanks_box.setWindowTitle('Thanks!')
                thanks_box.setText('Thanks for considering a donation!')


                thanks_box.exec_()

    def toggle_maximized(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'offset'):
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.parent().move(x - x_w, y - y_w)

    def draggable(self, enable=True):
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
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.parent().move(x - x_w, y - y_w)

    def apply_button_style(self, button):
        button.setStyleSheet(
            """
            QPushButton {
                border: none;
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: #555555;
                border-radius: 5px;
                padding: 2px;
            }

            QPushButton:hover {
                background-color: #666666;
            }
            """
        )


class RoundWindow(QFrame):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Roblox Quick Chat")
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(300, 200)

        self.set_background_image("Background_Image.webp")

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)

        title_bar = TitleBar(self)
        title_bar.customTextFileSelected.connect(self.load_custom_text_file)
        layout.addWidget(title_bar)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.content_widget = QWidget(scroll_area)
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 10, 0)
        self.content_layout.setSpacing(5)

        self.load_default_messages()

        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)

        layout.addWidget(scroll_area)

        self.set_rounded_edges()

        layout.setAlignment(Qt.AlignTop)
        self.draggable(True)

        self.show()

    def load_custom_text_file(self, file_path):
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    self.content_layout.removeWidget(widget)
                    widget.setParent(None)
    
        messages = []
        with open(file_path, 'r') as file:
            messages = [line.strip() for line in file.readlines()]
    
        num_messages = len(messages)
        num_columns = 3
        num_rows = (num_messages + num_columns - 1) // num_columns
    
        for i in range(num_rows):
            for j in range(num_columns):
                index = i * num_columns + j
                if index < num_messages:
                    button = QPushButton(messages[index])
                    self.apply_style(button)
                    button.clicked.connect(lambda _, m=messages[index]: self.on_message_click(m))
                    self.content_layout.addWidget(button, i, j)
                else:
                    placeholder = QWidget()
                    self.content_layout.addWidget(placeholder, i, j)

        self.content_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), num_rows, 0, 1, num_columns)
    def load_default_messages(self):
        messages = []
        with open('messages.txt', 'r') as file:
            messages = [line.strip() for line in file.readlines()]

        for i, message in enumerate(messages):
            button = QPushButton(message)
            self.apply_style(button)
            button.clicked.connect(lambda _, m=message: self.on_message_click(m))
            self.content_layout.addWidget(button, i // 3, i % 3)

    def focusInEvent(self, event):
        pass

    def on_message_click(self, message):
        worker_thread = WorkerThread()
        worker_thread.message = message
        worker_thread.start()

    def set_rounded_edges(self):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def draggable(self, enable=True):
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
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x - x_w, y - y_w)

    def apply_style(self, button):
        full_message = button.text()
        button.setStyleSheet(
            """
            QPushButton {
                border: none;
                padding: 10px 5px;
                font-size: 10pt;
                background-color: #555555;
                color: black;
                border-radius: 5px;
                max-width: 100px;
            }
            """
        )
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        def truncate_text(text, max_length):
            return text if len(text) <= max_length else text[:max_length - 3] + "..."

        truncated_text = truncate_text(full_message, 11)
        button.setText(truncated_text)
        button.setToolTip(full_message)

    def set_background_image(self, image_path):
        palette = QPalette()
        background_image = QPixmap(image_path)

        background_image = background_image.scaled(self.width(), self.height(), Qt.KeepAspectRatio)

        palette.setBrush(QPalette.Window, QBrush(background_image))
        self.setPalette(palette)

    def on_message_click(self, message):
        worker_thread = WorkerThread()
        worker_thread.message = message
        worker_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoundWindow()
    sys.exit(app.exec_())
