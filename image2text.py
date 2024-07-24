import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
import pytesseract

class ImageToTextApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('이미지 텍스트 추출기')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.select_button = QPushButton('이미지 선택', self)
        self.select_button.clicked.connect(self.select_image)
        layout.addWidget(self.select_button)

        self.convert_button = QPushButton('텍스트 추출', self)
        self.convert_button.clicked.connect(self.convert_image)
        layout.addWidget(self.convert_button)

        self.result_text = QTextEdit(self)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
            self.image_path = file_name

    def convert_image(self):
        if hasattr(self, 'image_path'):
            try:
                with Image.open(self.image_path) as img:
                    # Tesseract에 한국어 설정 추가
                    text = pytesseract.image_to_string(img, lang='kor+eng')
                self.result_text.setPlainText(text)
            except Exception as e:
                self.result_text.setPlainText(f"오류 발생: {str(e)}")
        else:
            self.result_text.setPlainText("이미지를 먼저 선택해주세요.")

def main():
    app = QApplication(sys.argv)
    ex = ImageToTextApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()