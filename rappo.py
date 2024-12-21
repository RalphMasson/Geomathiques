from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QTransform, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance
import sys

class TransparentWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()

        # Charger et ajuster l'image (augmenter contraste et luminosité)
        pil_image = Image.open(image_path)
        enhancer_contrast = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer_contrast.enhance(2.0)  # Augmenter le contraste (facteur 2.0)

        enhancer_brightness = ImageEnhance.Brightness(enhanced_image)
        enhanced_image = enhancer_brightness.enhance(1.2)  # Augmenter la luminosité (facteur 1.2)

        # Convertir l'image améliorée en QPixmap
        self.original_pixmap = self.pil_to_pixmap(enhanced_image)
        self.current_pixmap = self.original_pixmap
        self.scale_factor = 1.0
        self.rotation_angle = 0

        # Configurer la fenêtre
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.original_pixmap.width(), self.original_pixmap.height())
        self.center_window()

        # Ajouter un QLabel pour afficher l'image
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap(self.current_pixmap)
        self.label.resize(self.current_pixmap.width(), self.current_pixmap.height())

        # Ajouter les boutons flottants
        self.zoom_in_button = QPushButton("+", self)
        self.zoom_out_button = QPushButton("-", self)
        self.rotate_left_button = QPushButton("←", self)
        self.rotate_right_button = QPushButton("→", self)

        # Connecter les boutons aux fonctions
        self.zoom_in_button.clicked.connect(lambda: self.scale_image(1.1))
        self.zoom_out_button.clicked.connect(lambda: self.scale_image(0.9))
        self.rotate_left_button.clicked.connect(lambda: self.rotate_image(-1))  # Rotation de 1° à gauche
        self.rotate_right_button.clicked.connect(lambda: self.rotate_image(1))  # Rotation de 1° à droite

        # Empêcher les boutons de recevoir le focus clavier
        for button in [self.zoom_in_button, self.zoom_out_button, self.rotate_left_button, self.rotate_right_button]:
            button.setFocusPolicy(Qt.NoFocus)

        # Styles des boutons
        button_style = """
            QPushButton {
                background-color: white;
                border: 1px solid black;
                border-radius: 15px;
                font-size: 18px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: lightgray;
            }
        """
        self.zoom_in_button.setStyleSheet(button_style)
        self.zoom_out_button.setStyleSheet(button_style)
        self.rotate_left_button.setStyleSheet(button_style)
        self.rotate_right_button.setStyleSheet(button_style)

        self.zoom_in_button.resize(30, 30)
        self.zoom_out_button.resize(30, 30)
        self.rotate_left_button.resize(30, 30)
        self.rotate_right_button.resize(30, 30)

        self.update_button_positions()

        # Déplacer la fenêtre
        self.offset = None

    def pil_to_pixmap(self, pil_image):
        """
        Convertir une image Pillow en QPixmap.
        """
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        width, height = pil_image.size
        return QPixmap.fromImage(QImage(data, width, height, QImage.Format_RGBA8888))

    def keyPressEvent(self, event):
        """
        Gestion des événements clavier pour zoom et rotation.
        """
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
        elif event.key() == Qt.Key_Escape:  # Quitter
            self.close()

    def mousePressEvent(self, event):
        """
        Capture le clic pour déplacer la fenêtre.
        """
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """
        Déplacement de la fenêtre.
        """
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        """
        Fin du déplacement de la fenêtre.
        """
        if event.button() == Qt.LeftButton:
            self.offset = None

    def scale_image(self, scale_factor):
        """
        Zoomer/dézoomer l'image.
        """
        self.scale_factor *= scale_factor
        self.update_image()

    def rotate_image(self, angle):
        """
        Tourner l'image autour de son centre.
        """
        self.rotation_angle += angle
        self.update_image()

    def update_image(self):
        """
        Appliquer zoom et rotation à l'image.
        """
        # Appliquer la rotation autour du centre
        transform = QTransform()
        transform.translate(self.original_pixmap.width() // 2, self.original_pixmap.height() // 2)
        transform.rotate(self.rotation_angle)
        transform.translate(-self.original_pixmap.width() // 2, -self.original_pixmap.height() // 2)
        rotated_pixmap = self.original_pixmap.transformed(transform, Qt.SmoothTransformation)

        # Appliquer le zoom
        zoomed_pixmap = rotated_pixmap.scaled(
            int(self.original_pixmap.width() * self.scale_factor),
            int(self.original_pixmap.height() * self.scale_factor),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        # Mettre à jour l'image affichée
        self.current_pixmap = zoomed_pixmap
        self.label.setPixmap(self.current_pixmap)
        self.label.resize(self.current_pixmap.width(), self.current_pixmap.height())
        self.resize(self.label.width(), self.label.height())

        # Mettre à jour la position des boutons
        self.update_button_positions()

    def update_button_positions(self):
        """
        Positionner les boutons flottants au centre de l'image.
        """
        center_x = self.width() // 2
        center_y = self.height() // 2

        self.zoom_in_button.move(center_x - 80, center_y)
        self.zoom_out_button.move(center_x - 40, center_y)
        self.rotate_left_button.move(center_x + 10, center_y)
        self.rotate_right_button.move(center_x + 50, center_y)

    def center_window(self):
        """
        Centre la fenêtre sur l'écran.
        """
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    image_path = r"C:\Users\MASSON\Downloads\rapporteur4.png"  # Remplace par le chemin de ton image
    window = TransparentWindow(image_path)
    window.show()
    sys.exit(app.exec_())
