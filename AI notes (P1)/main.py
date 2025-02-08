import tkinter as tk
from tkinter import messagebox, colorchooser
from tkinter import ttk
from PIL import Image, ImageDraw
import google.generativeai as genai

# Initialize the AI model (Gemini)
genai.configure(api_key=" YOUR API KEY ") #change to your gemini api key
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = (
    "give answer to only one of the following situations, if any situation matches do not tell any other scenarios:"
    "if the image has any math problem, show the answer first, then give the explanation step by step in math matical form only."
    "if The image contains only a single number then write multiplication table of that number."
    "If the image has any cricket-based problem, analyze the total runs scored. Each color represents how many runs, so analyze the total different colored lines on the ground based on the number of lines in ground fig."
    "You must solve any trigonometric problem in the image."
    "if the image has some scenarios you check a perfect historical scenario to that image you have described it. For example, an apple falls on the head of a man then it will be Newton's law of universal gravitation."
    "The image may have some famous logos of apps, brands, etc. You have to tell the story behind that logo."
    "If the image is not blank, try to identify it."
    "If the image is blank, ask the user to draw something."
)

class MathSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Solver")

        # Create a main frame for scrolling
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Add canvas for scrolling
        self.scroll_canvas = tk.Canvas(main_frame)
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.scroll_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        self.scroll_canvas.bind('<Configure>', lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))

        # Add a frame inside the canvas for content
        self.content_frame = tk.Frame(self.scroll_canvas)
        self.scroll_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Canvas for drawing
        self.canvas_width = 1200
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.content_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)

        # Image for drawing operations
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

        # Current color for drawing
        self.current_color = "black"

        # Action stacks for undo/redo
        self.actions = []
        self.redo_stack = []

        # Bind mouse events for drawing
        self.canvas.bind("<B1-Motion>", self.paint)

        # Frame for buttons (right-aligned)
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Buttons aligned to the right
        self.solve_button = tk.Button(button_frame, text="Solve", command=self.process_image, bg="green", fg="white")
        self.solve_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_canvas, bg="red", fg="white")
        self.clear_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.color_button = tk.Button(button_frame, text="Choose Color", command=self.choose_color, bg="blue", fg="white")
        self.color_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.undo_button = tk.Button(button_frame, text="Undo", command=self.undo, bg="orange", fg="white")
        self.undo_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.redo_button = tk.Button(button_frame, text="Redo", command=self.redo, bg="purple", fg="white")
        self.redo_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Output section
        self.output_label = tk.Label(self.content_frame, text="Output:", font=("Arial", 14))
        self.output_label.pack(pady=5)

        self.output_text = tk.Text(self.content_frame, wrap=tk.WORD, height=10, width=80)
        self.output_text.pack(padx=10, pady=10)

    def paint(self, event):
        """Capture drawing events on the canvas."""
        x, y = event.x, event.y
        r = 5  # Brush size
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.current_color, outline=self.current_color)
        self.draw.ellipse([x - r, y - r, x + r, y + r], fill=self.current_color, outline=self.current_color)
        self.actions.append((x, y, self.current_color))  # Save action for undo
        self.redo_stack.clear()  # Clear redo stack after a new action

    def clear_canvas(self):
        """Clear the canvas and reset the drawing."""
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.output_text.delete(1.0, tk.END)
        self.actions.clear()
        self.redo_stack.clear()

    def choose_color(self):
        """Open a color chooser dialog to select the drawing color."""
        color_code = colorchooser.askcolor(title="Choose a color")[1]
        if color_code:
            self.current_color = color_code

    def undo(self):
        """Undo the last drawing action."""
        if self.actions:
            last_action = self.actions.pop()
            self.redo_stack.append(last_action)
            self.redraw_canvas()

    def redo(self):
        """Redo the last undone drawing action."""
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.actions.append(action)
            x, y, color = action
            r = 5  # Brush size
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=color)
            self.draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=color)

    def redraw_canvas(self):
        """Redraw the canvas based on the action stack."""
        self.clear_canvas()
        for x, y, color in self.actions:
            r = 5  # Brush size
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=color)
            self.draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=color)

    def process_image(self):
        """Send the canvas data to the AI model for processing."""
        try:
            output = self.send_to_ai(self.image)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process the image: {str(e)}")

    def send_to_ai(self, image):
        """Send the image to the AI model and get the response."""
        response = model.generate_content(
            [prompt, image]
        )
        return response.text if response else "No response from AI."

# Initialize the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MathSolverApp(root)
    root.mainloop()
