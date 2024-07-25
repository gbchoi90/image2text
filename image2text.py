import sys
import cv2
import numpy as np
import pytesseract
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QCheckBox
from PyQt5.QtGui import QDropEvent, QDragEnterEvent
from PyQt5.QtCore import Qt
import re
from PyPDF2 import PdfReader
import os

class AdvancedTextExtractorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.is_handwriting = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('고급 텍스트 추출기 (이미지, PDF 및 손글씨)')
        self.setGeometry(100, 100, 400, 350)
        self.setAcceptDrops(True)

        layout = QVBoxLayout()
        self.label = QLabel('이미지, PDF 또는 손글씨 이미지 파일을 드래그 앤 드롭하세요', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.handwriting_checkbox = QCheckBox('손글씨 모드', self)
        self.handwriting_checkbox.stateChanged.connect(self.toggle_handwriting_mode)
        self.button = QPushButton('텍스트 추출', self)
        self.button.clicked.connect(self.extract_text)
        self.textEdit = QTextEdit(self)

        for widget in (self.label, self.handwriting_checkbox, self.button, self.textEdit):
            layout.addWidget(widget)

        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.file_path = files[0]
            self.label.setText(f'선택된 파일: {self.file_path}')

    def toggle_handwriting_mode(self, state):
        self.is_handwriting = state == Qt.Checked

    def extract_text(self):
        if not self.file_path:
            self.show_message('오류', '파일을 먼저 드래그 앤 드롭하세요.')
            return

        try:
            file_extension = os.path.splitext(self.file_path)[1].lower()
            if file_extension == '.pdf':
                extracted_text = self.extract_text_from_pdf(self.file_path)
            elif file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                extracted_text = self.extract_text_from_image(self.file_path)
            else:
                raise ValueError("지원되지 않는 파일 형식입니다.")

            processed_text = self.postprocess_text(extracted_text)
            self.textEdit.setText(processed_text)
        except Exception as e:
            self.show_message('오류', f'텍스트 추출 중 오류 발생: {str(e)}')

    def extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def extract_text_from_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"이미지를 불러올 수 없습니다: {image_path}")

        # 이미지 전처리
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.is_handwriting:
            # 손글씨 모드일 때 추가 전처리
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        else:
            # 일반 텍스트 모드
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # OCR 설정
        config = '--oem 3 --psm 6'
        if self.is_handwriting:
            config += ' -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ가나다라마바사아자차카타파하'

        return pytesseract.image_to_string(gray, lang='kor+eng', config=config)

    @staticmethod
    def postprocess_text(text):
        # 기존의 후처리 로직 유지
        text = re.sub(r'(?<=[\u3131-\u3163\uac00-\ud7a3]) (?=[\u3131-\u3163\uac00-\ud7a3])', '', text)
        text = re.sub(r'(\d) (\d)', r'\1\2', text)
        text = re.sub(r'([가-힣]) (이|가|을|를|의|에|로|와|과|나|도|께|에서|부터|까지|처럼|만큼|보다|라고|라는|라도|라면)', r'\1\2', text)
        text = re.sub(r'\s*([.,!?:;])\s*', r'\1 ', text)
        text = re.sub(r'\s*(\()\s*', r'\1', text)
        text = re.sub(r'\s*(\))\s*', r'\1 ', text)
        return re.sub(r' +', ' ', text).strip()

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AdvancedTextExtractorApp()
    ex.show()
    sys.exit(app.exec_())
