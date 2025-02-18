import sys
import google.generativeai as genai
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PIL import Image
import io

# Set up Google Gemini AI API (Replace with your API key)
API_KEY = " YOUR_API_KEY"
genai.configure(api_key=API_KEY)

class ScreenshotTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot & AI Recognition")
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout()
        self.button = QPushButton("Select & Capture Screenshot")
        self.button.clicked.connect(self.capture_screenshot)
        layout.addWidget(self.button)

        self.result_label = QLabel("AI Result: ")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)

    def capture_screenshot(self):
        """Allows the user to select an area of the screen and process it."""
        self.hide()  # Hide the window while capturing
        
        screenshot = QApplication.primaryScreen().grabWindow(0)  # Take full screenshot
        img_path = "screenshot.png"
        screenshot.save(img_path, "PNG")  # Save screenshot

        self.show()  # Show the window again
        
        # Process and send to AI
        self.send_to_ai(img_path)

    def send_to_ai(self, img_path):
        """Sends the image to Gemini AI with a text prompt and updates the result."""
        with open(img_path, "rb") as img_file:
            image_data = img_file.read()
        
        # Convert to PIL image format
        img = Image.open(io.BytesIO(image_data))

        # **Use the latest Gemini model**
        model = genai.GenerativeModel("gemini-1.5-flash")  # **UPDATED MODEL**

        # **Add a text prompt along with the image**
        response = model.generate_content(["give answer to the quetion in the image.", img])

        # Update UI with AI response
        self.result_label.setText(f"AI Result: {response.text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotTool()
    window.show()
    sys.exit(app.exec_())
