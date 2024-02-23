import sys
import os

from PySide6.QtCore import Qt, QThread, QObject, Signal
from PySide6.QtGui import QIcon, QShortcut, QKeySequence
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                               QLabel, QSpinBox, QLineEdit, QListWidget, QPushButton, QListWidgetItem,
                               QMessageBox, QProgressDialog
                               )

from image import CustomImage

NOM_QSS = "style_docS.qss" #entrer le nom du fichier QSS à appliquer

class Worker(QObject):
    finished = Signal()
    image_converted =Signal(object, bool)
    
    def __init__(self, images_to_convert, quality, size, folder):
        super().__init__()
        self.images_to_convert = images_to_convert
        self.quality = quality
        self.size = size
        self.folder = folder
        self.runs = True
    
    def convert_images(self):
        for image_lw_item in self.images_to_convert:
            if self.runs and not image_lw_item.processed:
                image = CustomImage(path=image_lw_item.text(), folder=self.folder)
                success = image.reduce_image(size=self.size, quality=self.quality)
                self.image_converted.emit(image_lw_item, success)
                
        self.finished.emit()        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setWindowTitle("Convertisseur d'images")
        self.setFixedSize(500,400)
    
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
        
    def setup_ui(self):
        self.create_widgets()
        self.create_layouts()
        self.modify_widgets()
        self.add_widgets_to_layouts()
        self.setup_connections()
            
    def create_widgets(self):
        self.lbl_quality = QLabel("Qualité :")
        self.spn_quality = QSpinBox()
        self.lbl_size = QLabel("Taille : ")
        self.spn_size = QSpinBox()
        self.lbl_dossier_out = QLabel("Dossier de sortie :")
        self.le_dossier_out = QLineEdit()
        self.lw_files = QListWidget()
        self.btn_convert = QPushButton("Conversion")
        self.lbl_drop_info = QLabel("^ Déposez les images sur l'interface ^")
        
    def create_layouts(self):
        self.main_layout = QGridLayout() 
        
    def modify_widgets(self):
        if NOM_QSS:
            dos_pars = os.path.dirname(__file__)
            fichier_qss = os.path.join(dos_pars, NOM_QSS)
            with open(fichier_qss ,"r") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        
        #Alignment
        self.spn_quality.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spn_size.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.le_dossier_out.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        #Range
        self.spn_quality.setRange(1,100)
        self.spn_quality.setValue(75)
        self.spn_size.setRange(1,100)
        self.spn_size.setValue(100)
        
        #Divers
        self.le_dossier_out.setPlaceholderText("Entrez le dossier de sortie...")
        self.le_dossier_out.setText("images_reduites")
        self.lbl_drop_info.setVisible(False)
        
        self.setAcceptDrops(True)
        self.lw_files.setAlternatingRowColors(True)
        self.lw_files.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_quality, 0, 0, 1, 1)
        self.main_layout.addWidget(self.spn_quality, 0, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_size, 1, 0, 1, 1)
        self.main_layout.addWidget(self.spn_size, 1, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_dossier_out, 2, 0, 1, 1)
        self.main_layout.addWidget(self.le_dossier_out, 2, 1, 1, 1)
        self.main_layout.addWidget(self.spn_quality, 2, 1, 1, 1)
        self.main_layout.addWidget(self.lw_files, 3, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_drop_info, 4, 0, 1, 2)
        self.main_layout.addWidget(self.btn_convert, 5, 0, 1, 2)
        
    def setup_connections(self):
        QShortcut(QKeySequence("Del"), self.lw_files, self.delete_selected_items)
        self.btn_convert.clicked.connect(self.convert_images)
       
    # à partir d'ici les autres fonctions du programme
    def convert_images(self):
        quality = self.spn_quality.value()
        size = self.spn_size.value() / 100.0
        folder = self.le_dossier_out.text()
        
        lw_items = [self.lw_files.item(index) for index in range(self.lw_files.count())]
        images_a_convertir = [True for lw_item in lw_items if not lw_item.processed]
        if not images_a_convertir:
            msg_box = QMessageBox(QMessageBox.Icon.Warning,
                                  "Aucune image à convertir",
                                  "Toutes les images ont déja été converties")
            msg_box.exec()
            return False
        
        self.the_thread = QThread(self)
        self.worker = Worker(images_to_convert=lw_items,
                             quality=quality,
                             size=size,
                             folder=folder)
        
        self.worker.moveToThread(self.the_thread)
        self.worker.image_converted.connect(self.image_converted)
        self.the_thread.started.connect(self.worker.convert_images)
        self.worker.finished.connect(self.the_thread.quit)
        self.the_thread.start()
        
        self.prg_dialog = QProgressDialog("Conversion des images", "Annuler", 1, len(images_a_convertir))
        self.prg_dialog.canceled.connect(self.abord)
        self.prg_dialog.show()
        
    def abord(self):
        self.worker.runs = False
        self.the_thread.quit()
           
    def image_converted(self, lw_item, success):
        if success:
            lw_item.setIcon(QIcon(r"icones\valider.png"))
            lw_item.processed = True
            self.prg_dialog.setValue(self.prg_dialog.value() + 1 )
    
    def delete_selected_items(self):
        for lw_item in self.lw_files.selectedItems():
            row = self.lw_files.row(lw_item)
            self.lw_files.takeItem(row)
          
    def dragEnterEvent(self, event) :
        self.lbl_drop_info.setVisible(True)
        event.accept()
        
    def dragLeaveEvent(self, event):
        self.lbl_drop_info.setVisible(False)
        
    def dropEvent(self, event):
        event.accept()
        
        for url in event.mimeData().urls():
            self.add_file(path=url.toLocalFile())
            
        self.lbl_drop_info.setVisible(False)
    
    def add_file(self, path):
        items = [self.lw_files.item(index).text() for index in range(self.lw_files.count())]
        if path not in items:
            lw_item = QListWidgetItem(path)
            lw_item.setIcon(QIcon(r"icones\non_valider.png"))
            lw_item.processed = False
            self.lw_files.addItem(lw_item)
            
 
app = QApplication(sys.argv)
win = MainWindow()
win.show()
app.exec()