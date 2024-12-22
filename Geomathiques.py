import base64
from cryptography.fernet import Fernet

your_code = bytes("""
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QTransform, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance, ImageOps
import sys

class TransparentWindow(QMainWindow):
    def __init__(self, rapporteur_path, equerre_path):
        super().__init__()

        self.rapporteur_path = rapporteur_path
        self.equerre_path = equerre_path
        self.current_image_path = self.rapporteur_path  # Commence avec le rapporteur

        # Charger et ajuster l'image initiale
        self.load_and_enhance_image(self.current_image_path)
        # Taille initiale réduite pour l'équerre
        self.scale_factor = 0.3 if self.current_image_path == self.equerre_path else 1.0
        self.rotation_angle = 0

        # Configurer la fenêtre
        self.setAttribute(Qt.WA_TranslucentBackground)  # Transparence visuelle
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.resize(self.original_pixmap.width(), self.original_pixmap.height())
        self.center_window()
        self.setMouseTracking(True)  # Permet de suivre les mouvements de souris dans toute la fenêtre

        # Ajouter un QLabel pour afficher l'image
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap(self.current_pixmap)
        self.label.resize(self.current_pixmap.width(), self.current_pixmap.height())

        # Créer et styliser les boutons
        self.zoom_in_button = QPushButton("+", self)
        self.zoom_out_button = QPushButton("-", self)
        self.rotate_left_button = QPushButton("←", self)
        self.rotate_right_button = QPushButton("→", self)
        self.switch_button = QPushButton("Mode", self)
        self.flip_button = QPushButton("↻ 90°", self)

        # Redimensionner tous les boutons
        button_size = (70, 30)
        for button in [self.zoom_in_button, self.zoom_out_button,
                    self.rotate_left_button, self.rotate_right_button,
                    self.switch_button, self.flip_button]:
            button.resize(*button_size)

        # Connecter les boutons aux fonctions
        self.zoom_in_button.clicked.connect(lambda: self.scale_image(1.1))
        self.zoom_out_button.clicked.connect(lambda: self.scale_image(0.9))
        self.rotate_left_button.clicked.connect(lambda: self.rotate_image(-1))
        self.rotate_right_button.clicked.connect(lambda: self.rotate_image(1))
        self.switch_button.clicked.connect(self.switch_image)
        self.flip_button.clicked.connect(self.rotate_90_degrees)


        # Empêcher les boutons de recevoir le focus clavier
        for button in [self.zoom_in_button, self.zoom_out_button, self.rotate_left_button, self.rotate_right_button, self.switch_button, self.flip_button]:
            button.setFocusPolicy(Qt.NoFocus)

        for button in [self.zoom_in_button, self.zoom_out_button, self.rotate_left_button, self.rotate_right_button, self.switch_button]:
            button.setStyleSheet("background-color: white")
            button.setStyleSheet("border:1px solid black")
            button.setStyleSheet("border-radius: 15px")
            button.setStyleSheet("font-size:18px")
            button.setStyleSheet("padding:5px")

        self.zoom_in_button.resize(30, 30)
        self.zoom_out_button.resize(30, 30)
        self.rotate_left_button.resize(30, 30)
        self.rotate_right_button.resize(30, 30)
        self.switch_button.resize(70, 30)

        self.update_button_positions()

        self.installEventFilter(self)

        # Déplacer la fenêtre
        self.offset = None
        self.is_rotating = False
        self.update_image()

    def load_and_enhance_image(self, image_path):
        # Charger l'image avec Pillow
        pil_image = Image.open(image_path).convert("RGBA")  # Assurez-vous d'avoir un canal alpha

        # Rendre les pixels blancs semi-transparents
        data = pil_image.getdata()
        new_data = []
        for item in data:
            # Si le pixel est blanc (255, 255, 255), ajuster l'alpha
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                new_data.append((item[0], item[1], item[2], 2))  # Alpha = 128 (50% transparent)
            else:
                new_data.append(item)

        pil_image.putdata(new_data)

        # Améliorer contraste et luminosité
        enhancer_contrast = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer_contrast.enhance(2.0)  # Augmenter le contraste

        enhancer_brightness = ImageEnhance.Brightness(enhanced_image)
        enhanced_image = enhancer_brightness.enhance(1.2)  # Augmenter la luminosité

        # Convertir en QPixmap
        self.original_pixmap = self.pil_to_pixmap(enhanced_image)
        self.current_pixmap = self.original_pixmap

    def pil_to_pixmap(self, pil_image):

        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        width, height = pil_image.size
        return QPixmap.fromImage(QImage(data, width, height, QImage.Format_RGBA8888))

    def switch_image(self):

        self.current_image_path = self.equerre_path if self.current_image_path == self.rapporteur_path else self.rapporteur_path
        self.load_and_enhance_image(self.current_image_path)
        # Taille initiale ajustée
        self.scale_factor = 0.3 if self.current_image_path == self.equerre_path else 1.0
        self.update_image()

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
            self.rotate_90_degrees()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # Déplacement avec clic gauche
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
        elif event.button() == Qt.RightButton:  # Rotation avec clic droit
            self.is_rotating = True
            self.last_mouse_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.offset is not None:
            self.move(event.globalPos() - self.offset)
        elif event.buttons() == Qt.RightButton and self.is_rotating:
            current_pos = event.globalPos()
            delta = current_pos - self.last_mouse_pos
            self.last_mouse_pos = current_pos
            self.rotate_image(delta.x() * 0.2)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = None
        elif event.button() == Qt.RightButton:
            self.is_rotating = False

    def scale_image(self, scale_factor):

        self.scale_factor *= scale_factor
        self.update_image()

    def rotate_image(self, angle):

        self.rotation_angle += angle
        self.update_image()

    def confirm_exit(self):
        # Créer une boîte de dialogue de confirmation attachée à la fenêtre principale
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Quitter")
        msg_box.setText("Êtes-vous sûr de vouloir quitter ?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # Rendre la boîte de dialogue modale et afficher au-dessus
        msg_box.setWindowModality(Qt.ApplicationModal)

        # Afficher la boîte de dialogue et récupérer la réponse
        reply = msg_box.exec_()

        # Si l'utilisateur clique sur "Oui", fermer l'application
        if reply == QMessageBox.Yes:
            self.close()


    def update_image(self):
        transform = QTransform()
        transform.translate(self.original_pixmap.width() // 2, self.original_pixmap.height() // 2)
        transform.rotate(self.rotation_angle)
        transform.translate(-self.original_pixmap.width() // 2, -self.original_pixmap.height() // 2)
        rotated_pixmap = self.original_pixmap.transformed(transform, Qt.SmoothTransformation)

        zoomed_pixmap = rotated_pixmap.scaled(
            int(self.original_pixmap.width() * self.scale_factor),
            int(self.original_pixmap.height() * self.scale_factor),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.current_pixmap = zoomed_pixmap
        self.label.setPixmap(self.current_pixmap)
        self.label.resize(self.current_pixmap.width(), self.current_pixmap.height())

        # Augmenter la largeur de la fenêtre pour inclure les boutons
        extra_width = 90  # Largeur supplémentaire pour les boutons
        self.resize(self.label.width() + extra_width, self.label.height())
        self.update_button_positions()



    # Ajouter une méthode pour le flip
    def rotate_90_degrees(self):
        self.rotation_angle += 90  # Ajouter 90° à l'angle courant
        self.update_image()

    def update_button_positions(self):
        # Positionner les boutons à droite de l'image
        button_x = self.label.width() + 20  # Décalage horizontal pour être à droite de l'image
        button_y = 10  # Point de départ vertical
        spacing = 40  # Espacement vertical entre les boutons

        # Disposer les boutons verticalement
        self.zoom_in_button.move(button_x, button_y)
        self.zoom_out_button.move(button_x, button_y + spacing)
        self.rotate_left_button.move(button_x, button_y + 2 * spacing)
        self.rotate_right_button.move(button_x, button_y + 3 * spacing)
        self.switch_button.move(button_x, button_y + 4 * spacing)
        self.flip_button.move(button_x, button_y + 5 * spacing)

    def center_window(self):

        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

app = QApplication(sys.argv)

try:
    paths = sys._MEIPASS
    rapporteur_path = os.path.join(paths, 'rapporteur5.png')
    equerre_path = os.path.join(paths, 'pngegg.png')

except:
    rapporteur_path = r'C://Users//MASSON//Downloads//rapporteur5.png'  # Chemin de l'image du rapporteur
    equerre_path = r'C://Users//MASSON//Downloads//pngegg.png'  # Chemin de l'image de l'équerre

window = TransparentWindow(rapporteur_path, equerre_path)
window.show()
sys.exit(app.exec_())
""",'utf-8')
key = Fernet.generate_key()
encryption_type = Fernet(key)
encrypted_message = encryption_type.encrypt(your_code)

decrypted_message = encryption_type.decrypt(encrypted_message)

exec(decrypted_message)
