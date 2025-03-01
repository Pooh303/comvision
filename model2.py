import pickle
import cv2
import mediapipe as mp
import numpy as np
import time
import string

class SignLanguageModel2:
    def __init__(self, model_path='./model_best.p'):
        """
        Initializes the SignLanguageModel2 class.

        Args:
            model_path (str): Path to the trained model file (.p).
        """
        model_dict = pickle.load(open(model_path, 'rb'))
        self.model = model_dict['model']
        letters = string.ascii_uppercase.replace('J', '').replace('Z', '')
        self.labels_dict = {i: letter for i, letter in enumerate(letters)}

        # Setup Mediapipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, 
            max_num_hands=1, 
            min_detection_confidence=0.5,  # Lowered for better detection
            min_tracking_confidence=0.5
        )

        self.last_prediction = None
        self.last_prediction_time = 0
        self.confirmed_prediction = None

    def predict_and_draw(self, frame):
        """
        Predicts sign language letters and draws the results on the frame.

        Args:
            frame (np.ndarray): Camera frame.

        Returns:
            tuple: (frame, confirmed_prediction)
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            print("✅ Hand Detected!")  # Debugging

            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style(),
                )

                # Prepare data for prediction
                data_aux = []
                x_ = []
                y_ = []

                for landmark in hand_landmarks.landmark:
                    x = landmark.x
                    y = landmark.y
                    data_aux.append(x)
                    data_aux.append(y)
                    x_.append(x)
                    y_.append(y)

                if len(data_aux) == 42:  # Ensure correct data size
                    prediction = self.model.predict([np.asarray(data_aux)])
                    prob = self.model.predict_proba([np.asarray(data_aux)])

                    if prob is not None and len(prob) > 0:
                        predicted_character = self.labels_dict.get(np.argmax(prob), "")
                        confidence_score = np.max(prob)
                        self.update_prediction(predicted_character, confidence_score)

                        # Get hand bounding box
                        x1 = int(min(x_) * frame.shape[1]) - 10
                        y1 = int(min(y_) * frame.shape[0]) - 10
                        x2 = int(max(x_) * frame.shape[1]) + 10
                        y2 = int(max(y_) * frame.shape[0]) + 10

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

                        # Display prediction text
                        text = f"{self.confirmed_prediction}" if self.confirmed_prediction else f"{predicted_character} ({confidence_score:.2f})"
                        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
                    else:
                        print("⚠️ Warning: Empty prediction!")
                else:
                    print("⚠️ Warning: Incorrect landmark data size!")

        else:
            print("❌ No hand detected!")  # Debugging

        return frame, self.confirmed_prediction

    def update_prediction(self, predicted_character, confidence_score):
        """
        Updates the predicted letter with confirmation.

        Args:
            predicted_character (str): Predicted letter.
            confidence_score (float): Confidence score.
        """
        current_time = time.time()

        if confidence_score > 0.70:  # Confidence threshold
            if predicted_character == self.last_prediction:
                if current_time - self.last_prediction_time >= 2:  # Hold for 2 seconds
                    self.confirmed_prediction = predicted_character
            else:
                self.last_prediction = predicted_character
                self.last_prediction_time = current_time
        else:
            self.last_prediction = None
            self.last_prediction_time = 0
            self.confirmed_prediction = None
