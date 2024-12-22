import base64
from cryptography.fernet import Fernet

your_code = bytes("""
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QTransform, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance
import sys

class TransparentWindow(QMainWindow):
    BUTTON_SIZE = (70, 30)
    BUTTON_SPACING = 40
    TRANSPARENCY_ALPHA = 2

    def __init__(self, rapporteur_path, equerre_path):
        super().__init__()
        self.paths = {"rapporteur": rapporteur_path, "equerre": equerre_path}
        self.current_image_key = "rapporteur"
        self.rotation_angle = 0
        self.scale_factor = 1 if self.current_image_key == "equerre" else 1
        self.init_ui()
        self.load_and_display_image()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.label = QLabel(self)
        self.buttons = self.create_buttons()
        self.offset, self.is_rotating = None, False

    def create_buttons(self):
        button_configs = [
            ("+", lambda: self.scale_image(1.1)),
            ("-", lambda: self.scale_image(0.9)),
            ("←", lambda: self.rotate_image(-1)),
            ("→", lambda: self.rotate_image(1)),
            ("Mode", self.switch_image),
            ("↻ 90°", lambda: self.rotate_image(90)),
        ]
        buttons = []
        for i, (text, action) in enumerate(button_configs):
            button = QPushButton(text, self)
            button.resize(*self.BUTTON_SIZE)
            button.clicked.connect(action)
            button.setStyleSheet("background-color: white; border: 1px solid black; border-radius: 15px; font-size: 18px; padding: 5px;")
            button.setFocusPolicy(Qt.NoFocus)
            buttons.append(button)
        return buttons

    def load_and_display_image(self):
        pil_image = Image.open(self.paths[self.current_image_key]).convert("RGBA")
        self.current_pixmap = self.process_image(pil_image)
        self.label.setPixmap(self.current_pixmap)
        self.label.resize(self.current_pixmap.size())
        self.resize(self.label.width() + 90, self.label.height())
        self.update_button_positions()

    def process_image(self, pil_image):
        data = [
            (r, g, b, self.TRANSPARENCY_ALPHA if (r, g, b) == (255, 255, 255) else a)
            for r, g, b, a in pil_image.getdata()
        ]
        pil_image.putdata(data)
        pil_image = ImageEnhance.Contrast(pil_image).enhance(2.0)
        pil_image = ImageEnhance.Brightness(pil_image).enhance(1.2)
        return QPixmap.fromImage(QImage(pil_image.tobytes("raw", "RGBA"), *pil_image.size, QImage.Format_RGBA8888))

    def update_button_positions(self):
        button_x = self.label.width() + 20
        for i, button in enumerate(self.buttons):
            button.move(button_x, 10 + i * self.BUTTON_SPACING)

    def switch_image(self):
        self.current_image_key = "equerre" if self.current_image_key == "rapporteur" else "rapporteur"
        self.scale_factor = 1 if self.current_image_key == "equerre" else 1
        self.load_and_display_image()
        self.update_displayed_image()

    def scale_image(self, factor):
        self.scale_factor *= factor
        self.update_displayed_image()

    def rotate_image(self, angle):
        self.rotation_angle += angle
        self.update_displayed_image()

    def update_displayed_image(self):
        transform = QTransform()
        transform.translate(self.current_pixmap.width() // 2, self.current_pixmap.height() // 2)
        transform.rotate(self.rotation_angle)
        transform.translate(-self.current_pixmap.width() // 2, -self.current_pixmap.height() // 2)
        transformed_pixmap = self.current_pixmap.transformed(transform, Qt.SmoothTransformation)
        scaled_pixmap = transformed_pixmap.scaled(
            int(self.current_pixmap.width() * self.scale_factor),
            int(self.current_pixmap.height() * self.scale_factor),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.label.setPixmap(scaled_pixmap)
        self.label.resize(scaled_pixmap.size())
        self.resize(self.label.width() + 90, self.label.height())
        self.update_button_positions()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Plus:  # Zoom avant
            self.scale_image(1.1)
        elif event.key() == Qt.Key_Minus:  # Zoom arrière
            self.scale_image(0.9)
        elif event.key() == Qt.Key_Left:  # Rotation à gauche
            self.rotate_image(-1)
        elif event.key() == Qt.Key_Right:  # Rotation à droite
            self.rotate_image(1)
        elif event.key() == Qt.Key_Space:  # Rotation de 180°
            self.rotate_image(180)
        elif event.key() == Qt.Key_Escape:  # Quitter avec confirmation
            self.confirm_exit()
        elif event.key() == Qt.Key_M:  # Flip horizontal
            self.rotate_image(90)

    def confirm_exit(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Quitter")
        msg_box.setText("Êtes-vous sûr de vouloir quitter ?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg_box.exec_() == QMessageBox.Yes:
            self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
        elif event.button() == Qt.RightButton:
            self.is_rotating = True
            self.last_mouse_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.offset:
            self.move(event.globalPos() - self.offset)
        elif event.buttons() == Qt.RightButton and self.is_rotating:
            delta = event.globalPos() - self.last_mouse_pos
            self.last_mouse_pos = event.globalPos()
            self.rotate_image(delta.x() * 0.2)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = None
        elif event.button() == Qt.RightButton:
            self.is_rotating = False

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

try:
    paths = sys._MEIPASS
    rapporteur_path = os.path.join(paths, 'rapporteur.png')
    equerre_path = os.path.join(paths, 'equerre.png')

except:
    rapporteur_path = r'C://Users//MASSON//Downloads//Geomathiques//rapporteur.png'
    equerre_path = r'C://Users//MASSON//Downloads//Geomathiques//equerre.png'

app = QApplication(sys.argv)
window = TransparentWindow(rapporteur_path, equerre_path)
window.show()
sys.exit(app.exec_())
""",'utf-8')
key = Fernet.generate_key()
encryption_type = Fernet(key)
encrypted_message = encryption_type.encrypt(your_code)
decrypted_message = encryption_type.decrypt(encrypted_message)
exec(decrypted_message)
