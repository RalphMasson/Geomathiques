from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QComboBox,QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QTransform, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance
import sys

class TransparentWindow(QMainWindow):
    BUTTON_SIZE = (120, 30)
    BUTTON_SPACING = 40
    TRANSPARENCY_ALPHA = 2

    def __init__(self, rapporteur_path, equerre_path, regle_path):
        super().__init__()
        self.paths = {"rapporteur": rapporteur_path, "equerre": equerre_path, "regle": regle_path}
        self.current_image_key = "rapporteur"
        self.rotation_angle = {"rapporteur": 0, "equerre": 0, "regle": 0}
        self.scale_factor = {"rapporteur": 1, "equerre": 1, "regle": 1}
        self.dragged_label = None  # Label actuellement déplacé
        self.offset = None  # Décalage pour le déplacement
        self.is_rotating_label = None  # Label actuellement en rotation
        self.is_rotating = False  # Rotation de l'image principale
        self.last_mouse_pos = None  # Dernière position de la souris pour la rotation
        self.init_ui()
        self.load_and_display_image()

    def init_ui(self):

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # Conteneur principal
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Zone pour afficher l'image principale ou les outils multiples
        self.image_layout = QVBoxLayout()
        self.main_layout.addLayout(self.image_layout)

        # Labels pour chaque outil
        self.image_label = QLabel(self)  # Pour les images individuelles (rapporteur, équerre, règle)
        self.equerre_label = QLabel(self)  # Pour l'équerre (si utilisée avec règle)
        self.regle_label = QLabel(self)  # Pour la règle (si utilisée avec équerre)

        # Ajouter le label principal
        self.image_layout.addWidget(self.image_label)

        # Zone pour les boutons
        self.button_layout = QVBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        # Ajouter les boutons
        self.buttons = self.create_buttons()
        for button in self.buttons:
            self.button_layout.addWidget(button)

        # Ajuster les espaces
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(20)
        self.button_layout.setAlignment(Qt.AlignTop)


    def create_buttons(self):
        button_configs = [
            ("+", lambda: self.scale_image(1.1)),
            ("-", lambda: self.scale_image(0.9)),
            ("←", lambda: self.rotate_image( -1)),
            ("→", lambda: self.rotate_image(1)),
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

        self.combo_box = QComboBox(self)
        self.combo_box.addItems(["Rapporteur", "Équerre", "Règle", "Équerre + Règle"])
        self.combo_box.setStyleSheet("background-color: white; border: 1px solid black; border-radius: 15px; font-size: 16px; padding: 5px;")
        self.combo_box.setFixedWidth(120)
        self.combo_box.setFocusPolicy(Qt.NoFocus)
        self.combo_box.currentTextChanged.connect(self.switch_image)
        buttons.append(self.combo_box)

        return buttons



    def load_and_display_image(self):
        '''
        Charge l'image actuelle, applique des transformations, et ajuste la taille de la fenêtre.
        '''

        pil_image = Image.open(self.paths[self.current_image_key]).convert("RGBA")
        self.current_pixmap = self.process_image(pil_image)
        self.image_label.setPixmap(self.current_pixmap)
        self.image_label.resize(self.current_pixmap.size())


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

    def adjust_window_size(self):
        """
        Ajuste dynamiquement la taille de la fenêtre pour que l'équerre et la règle
        soient entièrement visibles.
        """
        # Calculer les limites des outils (équerre et règle)
        equerre_rect = self.equerre_label.geometry()
        regle_rect = self.regle_label.geometry()

        # Trouver les limites maximales
        max_width = max(equerre_rect.right(), regle_rect.right()) + 20  # +20 pour un peu de marge
        max_height = max(equerre_rect.bottom(), regle_rect.bottom()) + 20  # +20 pour un peu de marge

        # Ajuster la taille de la fenêtre
        self.setMinimumSize(max_width, max_height)
        self.resize(max(self.width(), max_width), max(self.height(), max_height))


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
        '''
        Positionne les boutons sur le côté droit de l'image.
        '''
        button_x = self.labels[self.current_image_key].width() + 20  # Décalage horizontal
        for i, button in enumerate(self.buttons):
            button.move(button_x, 10 + i * self.BUTTON_SPACING)

    def create_composite_image(self, key1, key2):
        """
        Crée une image composite en combinant deux outils (équerre et règle).
        Les images sont superposées avec une certaine distance.
        """
        image1 = Image.open(self.paths[key1]).convert("RGBA")
        image2 = Image.open(self.paths[key2]).convert("RGBA")

        # Définir une taille pour la nouvelle image composite
        max_width = max(image1.width, image2.width)
        total_height = image1.height + image2.height + 20  # +20 pour espacement

        # Créer une image vide pour la combinaison
        composite_image = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 0))

        # Coller les deux images sur la nouvelle image
        composite_image.paste(image1, (0, 0))  # Coller la première image en haut
        composite_image.paste(image2, (0, image1.height + 20))  # Coller la deuxième image en dessous

        # Sauvegarder temporairement l'image composite pour l'utiliser dans l'affichage
        composite_path = "composite_image.png"
        composite_image.save(composite_path)
        self.paths["equerre + regle"] = composite_path

    def switch_image(self, tool_name):
        if tool_name == "Équerre + Règle":
            self.current_image_key = "equerre + regle"

            # Charger et traiter les images de l'équerre et de la règle
            equerre_image = Image.open(self.paths["equerre"]).convert("RGBA")
            regle_image = Image.open(self.paths["regle"]).convert("RGBA")

            equerre_pixmap = self.process_image(equerre_image)
            regle_pixmap = self.process_image(regle_image)

            # Configurer les labels individuels avec transparence
            self.equerre_label.setPixmap(equerre_pixmap)
            self.equerre_label.resize(equerre_pixmap.size())
            self.equerre_label.move(50, 50)  # Position de départ pour l'équerre
            self.equerre_label.show()

            self.regle_label.setPixmap(regle_pixmap)
            self.regle_label.resize(regle_pixmap.size())
            self.regle_label.move(300, 150)  # Position de départ pour la règle
            self.regle_label.show()

            # Masquer le label principal
            self.image_label.hide()

            # Ajuster la taille de la fenêtre pour inclure les deux outils
            self.adjust_window_size()
        else:
            # Afficher l'image unique dans le label principal
            key_map = {"Rapporteur": "rapporteur", "Équerre": "equerre", "Règle": "regle"}
            self.current_image_key = key_map.get(tool_name, "rapporteur")

            self.load_and_display_image()

            # Masquer les labels individuels
            self.equerre_label.hide()
            self.regle_label.hide()
            self.image_label.show()




    def update_displayed_image(self):
        """
        Met à jour l'affichage de l'image avec les transformations appliquées (zoom, rotation).
        On part toujours de l'image d'origine pour éviter l'accumulation d'erreurs.
        """

        # 1. Zoomer d'abord sur l'image d'origine
        scaled_base = self.current_pixmap.scaled(
            int(self.current_pixmap.width() * self.scale_factor[self.current_image_key]),
            int(self.current_pixmap.height() * self.scale_factor[self.current_image_key]),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        # 2. Appliquer la rotation autour du centre de l'image zoomée
        transform = QTransform()
        transform.translate(scaled_base.width() // 2, scaled_base.height() // 2)
        transform.rotate(self.rotation_angle[self.current_image_key])
        transform.translate(-scaled_base.width() // 2, -scaled_base.height() // 2)

        final_pixmap = scaled_base.transformed(transform, Qt.SmoothTransformation)

        # 3. Mettre à jour l'affichage
        self.image_label.setPixmap(final_pixmap)
        self.image_label.resize(final_pixmap.size())
        self.resize(self.image_label.width() + 90, self.image_label.height())


    def scale_image(self, factor):
        """
        Applique un zoom à l'image active (label principal ou outil sélectionné dans le mode "Équerre + Règle").
        """
        if self.current_image_key == "equerre + regle" and self.active_label:
            # Zoom sur l'équerre ou la règle selon l'outil actif
            if self.active_label == self.equerre_label:
                key = "equerre"
            elif self.active_label == self.regle_label:
                key = "regle"
            else:
                return

            # Appliquer le zoom
            pixmap = QPixmap(self.paths[key])
            scaled_pixmap = pixmap.scaled(
                int(pixmap.width() * self.scale_factor[key] * factor),
                int(pixmap.height() * self.scale_factor[key] * factor),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            # Mettre à jour le label et la taille de l'outil
            self.scale_factor[key] *= factor
            self.active_label.setPixmap(scaled_pixmap)
            self.active_label.resize(scaled_pixmap.size())

            # Ajuster la fenêtre pour inclure l'outil redimensionné
            self.adjust_window_size()
        else:
            # Zoom sur l'image principale dans les autres modes
            self.scale_factor[self.current_image_key] *= factor
            self.update_displayed_image()


    def rotate_image(self, angle):
        self.rotation_angle[self.current_image_key] += angle
        # self.update_tool_image(tool_key)
        self.update_displayed_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus:
            self.scale_image(1.1)  # Zoom avant
        elif event.key() == Qt.Key_Minus:
            self.scale_image(0.9)  # Zoom arrière
        elif event.key() == Qt.Key_Left:
            if self.current_image_key != "equerre + regle":
                self.rotate_image(-1)  # Rotation de l'image principale
        elif event.key() == Qt.Key_Right:
            if self.current_image_key != "equerre + regle":
                self.rotate_image(1)  # Rotation de l'image principale
        elif event.key() == Qt.Key_Space:
            if self.current_image_key == "equerre + regle":
                # Rotation de 180° pour l'outil actif uniquement
                if self.active_label:
                    self.rotate_label(self.active_label, 180)
            else:
                self.rotate_image(180)  # Rotation de 180° pour l'image principale
        elif event.key() == Qt.Key_M:
            if self.current_image_key == "equerre + regle":
                # Rotation de 90° pour l'outil actif uniquement
                if self.active_label:
                    self.rotate_label(self.active_label, 90)
            else:
                self.rotate_image(90)  # Rotation de 90° pour l'image principale
        elif event.key() == Qt.Key_Escape:
            self.confirm_exit()  # Quitter l'application

    def apply_transparency(self, pil_image):
        """
        Applique la transparence à une image Pillow en rendant les pixels blancs ou proches du blanc semi-transparents.
        """
        data = []
        for r, g, b, a in pil_image.getdata():
            # Si le pixel est blanc ou proche du blanc, appliquer la transparence
            if (r, g, b) == (255, 255, 255):
                data.append((r, g, b, self.TRANSPARENCY_ALPHA))
            else:
                data.append((r, g, b, a))
        pil_image.putdata(data)
        return pil_image


    def rotate_label(self, label, angle):
        """
        Applique une rotation à un label spécifique (équerre ou règle) tout en conservant la transparence.
        """
        # Identifier la clé de l'outil actif
        if label == self.equerre_label:
            key = "equerre"
        elif label == self.regle_label:
            key = "regle"
        else:
            return

        # Charger l'image d'origine
        pil_image = Image.open(self.paths[key]).convert("RGBA")

        # Réappliquer la transparence au cas où il y ait des pixels blancs
        pil_image = self.apply_transparency(pil_image)

        # Effectuer la rotation en définissant un fond transparent
        new_angle = self.rotation_angle[key] + angle
        rotated_image = pil_image.rotate(
            new_angle,
            resample=Image.BICUBIC,
            expand=True,
            fillcolor=(0, 0, 0, 0)  # Fond 100 % transparent
        )

        # Convertir en QPixmap
        rotated_pixmap = QPixmap.fromImage(
            QImage(rotated_image.tobytes("raw", "RGBA"), rotated_image.width, rotated_image.height, QImage.Format_RGBA8888)
        )

        # Mettre à jour le label
        label.setPixmap(rotated_pixmap)
        label.resize(rotated_pixmap.size())

        # Mettre à jour l'angle
        self.rotation_angle[key] = new_angle





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
            # Mode "Équerre + Règle" : sélectionner un outil pour le déplacement ou le zoom
            if self.current_image_key == "equerre + regle":
                if self.equerre_label.geometry().contains(event.pos()):
                    self.dragged_label = self.equerre_label
                    self.active_label = self.equerre_label  # L'équerre devient l'outil actif
                    self.offset = event.pos() - self.equerre_label.pos()
                elif self.regle_label.geometry().contains(event.pos()):
                    self.dragged_label = self.regle_label
                    self.active_label = self.regle_label  # La règle devient l'outil actif
                    self.offset = event.pos() - self.regle_label.pos()
                else:
                    self.dragged_label = None
                    self.active_label = None
            else:
                # Mode avec une seule image : préparer le déplacement de la fenêtre entière
                self.offset = event.globalPos() - self.frameGeometry().topLeft()
                self.dragged_label = None
                self.active_label = None
        elif event.button() == Qt.RightButton:
            # Activer la rotation
            if self.current_image_key == "equerre + regle":
                if self.equerre_label.geometry().contains(event.pos()):
                    self.is_rotating_label = self.equerre_label
                elif self.regle_label.geometry().contains(event.pos()):
                    self.is_rotating_label = self.regle_label
                else:
                    self.is_rotating_label = None
                self.last_mouse_pos = event.globalPos()
            else:
                self.is_rotating = True
                self.last_mouse_pos = event.globalPos()


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # Déplacement d'un outil (équerre ou règle)
            if self.dragged_label:
                self.dragged_label.move(event.pos() - self.offset)
                if self.current_image_key == "equerre + regle":
                    self.adjust_window_size()  # Ajuster la fenêtre dynamiquement
            # Déplacement de la fenêtre dans les modes individuels
            elif self.offset and self.current_image_key != "equerre + regle":
                self.move(event.globalPos() - self.offset)
        elif event.buttons() == Qt.RightButton:
            # Rotation individuelle dans le mode "Équerre + Règle"
            if self.is_rotating_label:
                delta = event.globalPos() - self.last_mouse_pos
                self.last_mouse_pos = event.globalPos()
                # Rotation et réapplication de la transparence
                self.rotate_label(self.is_rotating_label, delta.x() * 0.2)
            elif self.is_rotating:
                # Rotation de l'image principale dans les autres modes
                delta = event.globalPos() - self.last_mouse_pos
                self.last_mouse_pos = event.globalPos()
                self.rotate_image(delta.x() * 0.2)


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragged_label = None
            self.offset = None
        elif event.button() == Qt.RightButton:
            self.is_rotating = False
            self.is_rotating_label = None


    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)


# Section principale pour lancer l'application
try:
    # Si l'application est exécutée via pyinstaller, récupérer les chemins d'accès aux images dans `_MEIPASS`
    paths = sys._MEIPASS
    rapporteur_path = os.path.join(paths, 'rapporteur.png')  # Chemin vers l'image du rapporteur
    equerre_path = os.path.join(paths, 'equerre.png')  # Chemin vers l'image de l'équerre
    regle_path = os.path.join(paths, 'regle.png')  # Chemin vers l'image de l'équerre

except:
    # Si l'application est exécutée directement, définir les chemins statiques
    rapporteur_path = r'C://Users//MASSON//Downloads//Geomathiques//rapporteur.png'
    equerre_path = r'C://Users//MASSON//Downloads//Geomathiques//equerre.png'
    regle_path = r'C://Users//MASSON//Downloads//Geomathiques//regle.png'


# Lancement de l'application
app = QApplication(sys.argv)
window = TransparentWindow(rapporteur_path, equerre_path, regle_path)
window.show()
sys.exit(app.exec_())