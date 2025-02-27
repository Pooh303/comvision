import cv2
import numpy as np
from scipy.spatial.distance import cdist
import mediapipe as mp

# --- 1. MediaPipe Setup ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# --- Desired Frame Size (for Display) ---
resize_width = 960
resize_height = 720

# --- 2. Video Capture ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# --- 3. "Z" Path (Coordinate List and Circles) ---
z_path_points = [
    (200, 150), (750, 150),  # Top line
    (200, 600), (750, 600), # Bottom line
]
z_path_points_array = np.array(z_path_points, dtype=np.int32)
# --- 4. Circle Parameters ---
circle_radius = 30
circle_color = (0, 255, 0)  # Green
circle_thickness = -1

circles_collected = [False] * len(z_path_points)

# --- 5. Store User's Drawing Points ---
user_drawing = []

# --- 6. Scoring Function ---
def calculate_score(user_drawing, z_path_points):
    """Calculates the score based on how close the user's drawing is to the Z path."""
    if not isinstance(user_drawing, np.ndarray) or user_drawing.size == 0:
        return 0.0, []

    z_path_points = np.array(z_path_points)
    distances = cdist(user_drawing, z_path_points)
    min_distances = np.min(distances, axis=1)
    avg_distance = np.mean(min_distances)
    max_possible_distance = np.sqrt(resize_width**2 + resize_height**2)
    score = max(0, 100 - (avg_distance / max_possible_distance) * 100)
    return score, min_distances
# --- 7. Main Loop ---
next_circle_index = 0
show_restart_button = False  # Flag to control button visibility
current_line = 0  # 0 for top, 1 for diagonal, 2 for bottom
user_drawing_points_for_line = []  # Store drawing points for each line

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (resize_width, resize_height))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    current_point = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Changed to INDEX_FINGER_TIP
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_finger_tip.x * resize_width)
            y = int(index_finger_tip.y * resize_height)
            current_point = (x, y)

            cv2.circle(frame, current_point, 10, (0, 0, 255), -1)

            if not show_restart_button:
              user_drawing.append(current_point)
              user_drawing_points_for_line.append(current_point)
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
    for i, (x, y) in enumerate(z_path_points):
        if not circles_collected[i]:
            if i == next_circle_index:
                if current_point is not None:
                    distance = np.sqrt((current_point[0] - x)**2 + (current_point[1] - y)**2)
                    if distance <= circle_radius:
                        circles_collected[i] = True
                        next_circle_index += 1

            draw_color = (0, 0, 255) if i == next_circle_index else circle_color
            cv2.circle(frame, (x, y), circle_radius, draw_color, circle_thickness)

    # --- Score and Restart Button Logic ---
    if all(circles_collected):
        score, min_distances = calculate_score(user_drawing, z_path_points)
        cv2.putText(frame, f"Score: {score:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        show_restart_button = True  # Show button after completion

        # Highlight problem areas
        for i, dist in enumerate(min_distances):
          if dist > circle_radius * 1.5:  # More forgiving threshold
              cv2.circle(frame, user_drawing[i], 5, (0, 0, 255), -1)

    if show_restart_button:
        # --- Draw a Simple Restart Button ---
        button_x = 50
        button_y = 100
        button_width = 150
        button_height = 50
        cv2.rectangle(frame, (button_x, button_y), (button_x + button_width, button_y + button_height), (255, 0, 0), -1)  # Blue button
        cv2.putText(frame, "Restart", (button_x + 10, button_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # --- Button Click Detection (using finger position) ---
        if current_point is not None:
            if button_x <= current_point[0] <= button_x + button_width and \
               button_y <= current_point[1] <= button_y + button_height:
                # Reset everything
                user_drawing = []
                circles_collected = [False] * len(z_path_points)
                next_circle_index = 0
                show_restart_button = False  # Hide the button
                user_drawing_points_for_line = []

    cv2.imshow('Finger Drawing', frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('c'):  # Clear (same as before)
        user_drawing = []
        circles_collected = [False] * len(z_path_points)
        next_circle_index = 0
        show_restart_button = False  # Hide the button
        user_drawing_points_for_line = []
        

hands.close()
cap.release()
cv2.destroyAllWindows()


