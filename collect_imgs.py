import os
import cv2

# รับค่า x จากผู้ใช้เพื่อระบุชื่อของโฟลเดอร์
x = int(input("Enter the starting folder number (e.g. 4): "))

# กำหนดพาธหลักที่ต้องการให้สร้าง
DATA_DIR = './data'

# ตรวจสอบว่า /data มีอยู่หรือไม่ หากไม่มีก็จะสร้าง
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 1 # จำนวนคลาสที่ต้องการ
dataset_size = 1000  # ขนาดของชุดข้อมูลที่ต้องการ

cap = cv2.VideoCapture(0)

# สร้างโฟลเดอร์ต่อจากหมายเลขที่ผู้ใช้ระบุ
for j in range(x, x + number_of_classes):
    class_folder = os.path.join(DATA_DIR, str(j))
    if not os.path.exists(class_folder):
        os.makedirs(class_folder)

    print(f'Collecting data for class {j}')

    done = False
    while True:
        ret, frame = cap.read()
        cv2.putText(frame, 'Ready? Press "Q" ! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3,
                    cv2.LINE_AA)
        cv2.imshow('frame', frame)
        if cv2.waitKey(25) == ord('q'):
            break

    counter = 0
    while counter < dataset_size:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        cv2.waitKey(25)
        # บันทึกรูปภาพในโฟลเดอร์ของแต่ละคลาส
        cv2.imwrite(os.path.join(class_folder, f'{counter}.jpg'), frame)
        counter += 1

cap.release()
cv2.destroyAllWindows()