import os
import cv2
import argparse
import time  # Import the time module

# --- Command-line arguments ---
parser = argparse.ArgumentParser(description="Collect images for sign language recognition.")
parser.add_argument("--num_static_classes", type=int, default=24, help="Number of static classes (A-I, K-Y)")
parser.add_argument("--num_dynamic_classes", type=int, default=2, help="Number of dynamic classes (J, Z)")  # J and Z
parser.add_argument("--dataset_size", type=int, default=100, help="Number of samples per class")
parser.add_argument("--sequence_length", type=int, default=10, help="Number of frames for dynamic signs (J, Z)")
parser.add_argument("--camera", type=int, default=0, help="Camera index (0 for default)")
parser.add_argument("--data_dir", type=str, default='./data', help="Data directory")
args = parser.parse_args()

DATA_DIR = args.data_dir
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Class indices ---
static_class_indices = list(range(args.num_static_classes))  # 0-23 (A-I, K-Y)
dynamic_class_indices = list(range(args.num_static_classes, args.num_static_classes + args.num_dynamic_classes))  # 24-25 (J, Z)

# --- Camera setup with error handling ---
cap = cv2.VideoCapture(args.camera)
if not cap.isOpened():
    print(f"Error: Could not open camera {args.camera}")
    exit()

# --- ROI definition ---
roi_x = 100
roi_y = 100
roi_width = 400
roi_height = 400

# --- Collect Static Signs ---
for class_index in static_class_indices:
    class_dir = os.path.join(DATA_DIR, str(class_index))
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    print(f'Collecting data for static class {class_index} ({class_index+1}/{args.num_static_classes + args.num_dynamic_classes})')

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        cv2.putText(frame, f'Ready for class {class_index}? Press "s" to start!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    counter = 0
    while counter < args.dataset_size:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (255, 0, 0), 2)
        cv2.putText(frame, f'Class: {class_index}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Image: {counter + 1}/{args.dataset_size}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, 'Press "c" to capture, "q" to quit', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            roi = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]
            image_path = os.path.join(class_dir, f'{counter:04d}.jpg')
            cv2.imwrite(image_path, roi)
            counter += 1
            print(f"Saved: {image_path}")

        elif key == ord('q'):
            break
    if counter < args.dataset_size:
        print(f"Collected {counter} of {args.dataset_size} images for static class {class_index}.")
# --- Collect Dynamic Signs ---
for class_index in dynamic_class_indices:
    class_dir = os.path.join(DATA_DIR, str(class_index))
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    print(f'Collecting data for dynamic class {class_index} ({class_index+1}/{args.num_static_classes + args.num_dynamic_classes})')

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        cv2.putText(frame, f'Ready for class {class_index}? Press "s" to start!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    counter = 0
    while counter < args.dataset_size:
        print(f'Recording sequence {counter + 1}/{args.dataset_size} for class {class_index}')
        sequence = []
        for _ in range(args.sequence_length):
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break  # Exit the inner loop
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (255, 0, 0), 2)
            cv2.putText(frame, f'Class: {class_index}, Recording...', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('frame', frame)
            cv2.waitKey(33)  # ~30 FPS, adjust as needed
            roi = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]
            sequence.append(roi)
        else:
            # Save all frames as a sequence of images (if the inner loop completed successfully)
           for i, frame_in_sequence in enumerate(sequence):
               image_path = os.path.join(class_dir, f'{counter:04d}_{i:02d}.jpg')
               cv2.imwrite(image_path, frame_in_sequence)
           counter += 1

        if cv2.waitKey(1) == ord("q"):
            break
    if counter < args.dataset_size:
      print(f"Collected {counter} of {args.dataset_size} sequence for dynamic class {class_index}.")

cap.release()
cv2.destroyAllWindows()
print("Data collection complete.")