import base64
from cryptography.fernet import Fernet

your_code = bytes("""
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QTransform, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance
import sys

class TransparentWindow(QMainWindow):
    '''
    Une fenêtre principale transparente qui permet d'afficher et de manipuler des images
    (rapporteur et équerre), avec des fonctionnalités comme zoom, rotation, et déplacement.
    '''

    BUTTON_SIZE = (70, 30)  # Taille par défaut des boutons
    BUTTON_SPACING = 40  # Espacement vertical entre les boutons
    TRANSPARENCY_ALPHA = 2  # Niveau de transparence pour les zones blanches des images

    def __init__(self, rapporteur_path, equerre_path):
        '''
        Initialise la fenêtre transparente.

        Args:
            rapporteur_path (str): Chemin vers l'image du rapporteur.
            equerre_path (str): Chemin vers l'image de l'équerre.
        '''
        super().__init__()
        self.paths = {"rapporteur": rapporteur_path, "equerre": equerre_path}
        self.current_image_key = "rapporteur"  # Image actuellement affichée
        self.rotation_angle = 0  # Angle de rotation de l'image
        self.scale_factor = 1  # Facteur de mise à l'échelle
        self.init_ui()
        self.load_and_display_image()

    def init_ui(self):
        '''
        Configure l'interface utilisateur, y compris les propriétés de la fenêtre,
        le QLabel pour l'image et les boutons flottants.
        '''
        # Configurer la fenêtre
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # Ajouter un QLabel pour afficher l'image
        self.label = QLabel(self)

        # Créer les boutons
        self.buttons = self.create_buttons()
        self.offset, self.is_rotating = None, False  # Initialiser les variables de déplacement et rotation

    def create_buttons(self):
        '''
        Crée les boutons pour les interactions (zoom, rotation, etc.).

        Returns:
            list: Liste des QPushButton créés.
        '''
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
            button.setFocusPolicy(Qt.NoFocus)  # Empêcher de prendre le focus clavier
            buttons.append(button)
        return buttons

    def load_and_display_image(self):
        '''
        Charge l'image actuelle (rapporteur ou équerre), applique des transformations,
        et met à jour l'affichage.
        '''
        pil_image = Image.open(self.paths[self.current_image_key]).convert("RGBA")
        self.current_pixmap = self.process_image(pil_image)
        self.label.setPixmap(self.current_pixmap)
        self.label.resize(self.current_pixmap.size())
        self.resize(self.label.width() + 90, self.label.height())  # Ajuster la taille de la fenêtre
        self.update_button_positions()

    def process_image(self, pil_image):
        '''
        Transforme l'image Pillow en QPixmap, en appliquant des ajustements de contraste,
        de luminosité, et de transparence.

        Args:
            pil_image (PIL.Image.Image): Image chargée avec Pillow.

        Returns:
            QPixmap: Image transformée et prête à être affichée.
        '''
        # Rendre les pixels blancs semi-transparents
        data = [
            (r, g, b, self.TRANSPARENCY_ALPHA if (r, g, b) == (255, 255, 255) else a)
            for r, g, b, a in pil_image.getdata()
        ]
        pil_image.putdata(data)

        # Ajuster le contraste et la luminosité
        pil_image = ImageEnhance.Contrast(pil_image).enhance(2.0)
        pil_image = ImageEnhance.Brightness(pil_image).enhance(1.2)

        return QPixmap.fromImage(QImage(pil_image.tobytes("raw", "RGBA"), *pil_image.size, QImage.Format_RGBA8888))

    def update_button_positions(self):
        '''
        Positionne les boutons sur le côté droit de l'image.
        '''
        button_x = self.label.width() + 20  # Décalage horizontal
        for i, button in enumerate(self.buttons):
            button.move(button_x, 10 + i * self.BUTTON_SPACING)

    def switch_image(self):
        '''
        Permet de passer de l'image du rapporteur à celle de l'équerre (et vice-versa).
        '''
        self.current_image_key = "equerre" if self.current_image_key == "rapporteur" else "rapporteur"
        self.load_and_display_image()
        self.update_displayed_image()

    def scale_image(self, factor):
        '''
        Modifie l'échelle de l'image.

        Args:
            factor (float): Facteur multiplicatif pour la mise à l'échelle.
        '''
        self.scale_factor *= factor
        self.update_displayed_image()

    def rotate_image(self, angle):
        '''
        Fait pivoter l'image d'un certain angle.

        Args:
            angle (float): Angle en degrés.
        '''
        self.rotation_angle += angle
        self.update_displayed_image()

    def update_displayed_image(self):
        '''
        Met à jour l'affichage de l'image avec les transformations appliquées (rotation, zoom).
        '''
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
        '''
        Gère les raccourcis clavier pour les actions de la fenêtre.

        Args:
            event (QKeyEvent): Événement clavier.
        '''
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

    def confirm_exit(self):
        '''
        Affiche une boîte de dialogue demandant confirmation avant de quitter.
        '''
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Quitter")
        msg_box.setText("Êtes-vous sûr de vouloir quitter ?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg_box.exec_() == QMessageBox.Yes:
            self.close()

    def mousePressEvent(self, event):
        '''
        Gère le clic de la souris pour déplacer ou faire pivoter la fenêtre.

        Args:
            event (QMouseEvent): Événement de clic souris.
        '''
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
        elif event.button() == Qt.RightButton:
            self.is_rotating = True
            self.last_mouse_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        '''
        Gère le mouvement de la souris pour le déplacement ou la rotation.

        Args:
            event (QMouseEvent): Événement de mouvement souris.
        '''
        if event.buttons() == Qt.LeftButton and self.offset:
            self.move(event.globalPos() - self.offset)
        elif event.buttons() == Qt.RightButton and self.is_rotating:
            delta = event.globalPos() - self.last_mouse_pos
            self.last_mouse_pos = event.globalPos()
            self.rotate_image(delta.x() * 0.2)

    def mouseReleaseEvent(self, event):
        '''
        Réinitialise les états après le relâchement d'un bouton de souris.

        Args:
            event (QMouseEvent): Événement de relâchement souris.
        '''
        if event.button() == Qt.LeftButton:
            self.offset = None
        elif event.button() == Qt.RightButton:
            self.is_rotating = False

    def center_window(self):
        '''
        Centre la fenêtre sur l'écran.
        '''
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

# Section principale pour lancer l'application
try:
    # Si l'application est exécutée via pyinstaller, récupérer les chemins d'accès aux images dans `_MEIPASS`
    paths = sys._MEIPASS
    rapporteur_path = os.path.join(paths, 'rapporteur.png')  # Chemin vers l'image du rapporteur
    equerre_path = os.path.join(paths, 'equerre.png')  # Chemin vers l'image de l'équerre
except:
    # Si l'application est exécutée directement, définir les chemins statiques
    rapporteur_path = r'C://Users//MASSON//Downloads//Geomathiques//rapporteur.png'
    equerre_path = r'C://Users//MASSON//Downloads//Geomathiques//equerre.png'

# Lancement de l'application
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
