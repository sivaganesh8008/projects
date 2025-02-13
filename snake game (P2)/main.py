import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# Initialize Camera
cap = cv2.VideoCapture(0)  # Change if needed
cap.set(3, 1920)  # Set width to 1920
cap.set(4, 1080)  # Set height to 1080

# Get screen resolution
screen_width = 1920
screen_height = 1080

# Initialize Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)


class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # all points of the snake
        self.lengths = []  # distance between each point
        self.currentLength = 0  # max length before removing tail
        self.allowedLength = 150  # total allowed Length
        self.previousHead = (0, 0)  # previous head position
        self.score = 0
        self.gameOver = False

        # Load Food Image
        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        if self.imgFood is None:
            raise FileNotFoundError(f"Could not load food image: {pathFood}")
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = (0, 0)
        self.randomFoodLocation()

    def randomFoodLocation(self):
        """Places food at a random location within bounds."""
        self.foodPoint = (random.randint(100, screen_width - 100), 
                          random.randint(100, screen_height - 100))

    def update(self, imgMain, currentHead):
        """Updates the snake game state with new head position."""
        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", (screen_width//3, screen_height//3), scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', (screen_width//3, screen_height//2), scale=7, thickness=5, offset=20)
            return imgMain

        px, py = self.previousHead
        cx, cy = currentHead

        # Ensure the first detected point is set correctly
        if not self.points:
            self.previousHead = (cx, cy)

        self.points.append((cx, cy))
        distance = math.hypot(cx - px, cy - py)
        self.lengths.append(distance)
        self.currentLength += distance
        self.previousHead = (cx, cy)

        # Trim Snake if Length Exceeds Allowed Limit
        while self.currentLength > self.allowedLength:
            self.currentLength -= self.lengths.pop(0)
            self.points.pop(0)

        # ✅ Check if snake eats food
        rx, ry = self.foodPoint
        if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                ry - self.hFood // 2 < cy < ry + self.hFood // 2:
            self.randomFoodLocation()
            self.allowedLength += 50
            self.score += 1

        # ✅ Draw Snake
        if self.points:
            for i in range(1, len(self.points)):
                cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
            cv2.circle(imgMain, self.points[-1], 20, (0, 255, 0), cv2.FILLED)

        # ✅ Draw Food
        imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))

        # ✅ Display Score
        cvzone.putTextRect(imgMain, f'Score: {self.score}', (50, 100), scale=3, thickness=3, offset=10)

        return imgMain

    def reset_game(self):
        """Resets the game state when 'r' is pressed."""
        self.gameOver = False
        self.points.clear()
        self.lengths.clear()
        self.currentLength = 0
        self.allowedLength = 150
        self.previousHead = (0, 0)
        self.randomFoodLocation()
    def quit(self):
        self.quit()


# Load Game with Food Image
game = SnakeGameClass("Donut.png")

cv2.namedWindow("Snake Game", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Snake Game", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    if not success:
        print("Camera read error")
        continue

    img = cv2.flip(img, 1)

    # Resize the image to fit full screen
    img = cv2.resize(img, (screen_width, screen_height))

    hands, img = detector.findHands(img, flipType=False)

    if hands:
        lmList = hands[0]['lmList']
        if len(lmList) > 8:
            pointIndex = (lmList[8][0], lmList[8][1])
            img = game.update(img, pointIndex)

    cv2.imshow("Snake Game", img)
    key = cv2.waitKey(1)

    # Press 'r' to restart
    if key == ord('q'):
        game.quit()
