import os
import mediapipe as mp
import cv2
import pickle
import numpy as np
import argparse

# --- Command-line arguments ---
parser = argparse.ArgumentParser(description="Create dataset from collected images.")
parser.add_argument("--data_dir", type=str, default='./data', help="Directory containing collected images.")
parser.add_argument("--output_file", type=str, default='data.pickle', help="Output pickle file name.")
parser.add_argument("--min_detection_confidence", type=float, default=0.3, help="Minimum hand detection confidence.")
parser.add_argument("--max_num_hands", type=int, default=1, help="Maximum number of hands to detect.")
parser.add_argument("--skip_no_detection", action='store_true', help="Skip images where no hands are detected.")
parser.add_argument("--sequence_length", type=int, default=10, help="Expected sequence length for dynamic signs.")
parser.add_argument("--num_static_classes", type=int, default=24, help="Number of static classes (A-I, K-Y)")
args = parser.parse_args()

# --- Mediapipe setup ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True,  # Still use static_image_mode
                      min_detection_confidence=args.min_detection_confidence,
                      max_num_hands=args.max_num_hands)

# --- Data and labels lists ---
data = []
labels = []

# --- Check data directory ---
if not os.path.exists(args.data_dir):
    print(f"Error: Data directory '{args.data_dir}' does not exist.")
    exit()

if not os.listdir(args.data_dir):
    print(f"Error: Data directory '{args.data_dir}' is empty.")
    exit()

# --- Augmentation functions ---
def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def translate_image(image, tx, ty):
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    result = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
    return result

def scale_image(image, scale_factor):
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    result = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return result

def augment_image(image):
    augmented_images = [image]
    for angle in [-15, 15]:
        augmented_images.append(rotate_image(image, angle))
    for tx, ty in [(-20, -20), (20, 20), (20, -20), (-20, 20)]:
        augmented_images.append(translate_image(image, tx, ty))
    for scale in [0.9, 1.1]:
        augmented_images.append(scale_image(image, scale))
    return augmented_images

# --- Landmark processing function ---
def process_landmarks(image, results):
    """Processes hand landmarks and returns normalized coordinates."""
    data_aux = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Normalize to wrist
            wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
            wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y

            for landmark in hand_landmarks.landmark:
                data_aux.append(landmark.x - wrist_x)
                data_aux.append(landmark.y - wrist_y)
    else:
        if not args.skip_no_detection:
          data_aux = [0.0] * (21*2) #Zero-padding

    return data_aux

# --- Main processing loop ---
for dirpath, dirnames, filenames in os.walk(args.data_dir):
    # We process directories differently based on whether they're for static or dynamic signs.
    dir_name = os.path.basename(dirpath)  # Get the directory name
    if dir_name.isdigit(): # Check if the directory name is a number.
        class_index = int(dir_name)
    else:
        continue  # Skip non-numeric directory names (like 'data')


    if class_index < args.num_static_classes:  # Static sign
        for filename in filenames:
            if not filename.endswith('.jpg'):
                continue

            file_path = os.path.join(dirpath, filename)
            print(f"Processing static: {file_path}")

            try:
                img = cv2.imread(file_path)
                if img is None:
                    print(f"Warning: Could not read image '{file_path}'. Skipping.")
                    continue

                img = cv2.resize(img, (640, 480))
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Augmentation
                augmented_images = augment_image(img_rgb)
                for img_aug in augmented_images:
                    results = hands.process(img_aug)
                    data_aux = process_landmarks(img_aug, results)

                    if data_aux:
                        data.append(data_aux)
                        labels.append(class_index)

            except Exception as e:
                print(f"Error processing '{file_path}': {e}")
                continue

    else:  # Dynamic sign
        # Group filenames by sequence ID (e.g., 0000_00.jpg, 0000_01.jpg -> sequence ID 0000)
        sequences = {}
        for filename in filenames:
            if filename.endswith('.jpg'):
                try:
                    base_name, _ = filename.split('_')  # Extract "0000" from "0000_00.jpg"
                    if base_name not in sequences:
                        sequences[base_name] = []
                    sequences[base_name].append(os.path.join(dirpath, filename))
                except:
                    print("Incorrect file name", filename)
                    continue

        # Process each sequence
        for base_name, file_paths in sequences.items():
            # Sort file paths within the sequence (important for correct order)
            file_paths.sort()

            if len(file_paths) != args.sequence_length:
                print(f"Warning: Sequence {base_name} has {len(file_paths)} frames (expected {args.sequence_length}). Skipping.")
                continue

            sequence_data = []
            valid_sequence = True
            for file_path in file_paths:
                print(f"Processing dynamic: {file_path}")
                try:
                    img = cv2.imread(file_path)
                    if img is None:
                        print(f"Warning: Could not read image '{file_path}'. Skipping sequence.")
                        valid_sequence = False
                        break

                    img = cv2.resize(img,(640,480))
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    results = hands.process(img_rgb)
                    data_aux = process_landmarks(img_rgb, results)

                    if data_aux:
                         sequence_data.extend(data_aux)  # Extend, not append, to flatten the sequence
                    else:
                        print("Invalid data, skipping sequence")
                        valid_sequence = False
                        break

                except Exception as e:
                    print(f"Error processing '{file_path}': {e}")
                    valid_sequence = False
                    break  # Exit inner loop on error

            if valid_sequence and sequence_data:  # Check if the sequence is complete and valid
               data.append(sequence_data)  # Append the flattened sequence data
               labels.append(class_index)

# --- Check for empty dataset ---
if not data:
    print("Error: No data collected. Check your data directory and image files.")
    exit()

# --- Save the data and labels ---
with open(args.output_file, 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print(f"Dataset created: {len(data)} samples saved to '{args.output_file}'.")