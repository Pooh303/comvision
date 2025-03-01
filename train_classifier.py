import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import numpy as np
from collections import Counter

# โหลดข้อมูล
data_dict = pickle.load(open('./data.pickle', 'rb'))
data = np.asarray(data_dict['data'])
labels = np.asarray(data_dict['labels'])

# ตรวจสอบจำนวนตัวอย่างในแต่ละคลาส
class_counts = Counter(labels)
print("จำนวนตัวอย่างในแต่ละแบบ:", class_counts)

# กำหนดจำนวน fold
k = 10
kf = KFold(n_splits=k, shuffle=True, random_state=42)

# ตัวแปรสำหรับเก็บผลลัพธ์
accuracy_scores = []

# เริ่มกระบวนการ k-fold cross-validation
for train_index, test_index in kf.split(data):
    # แบ่งข้อมูลออกเป็น training และ testing set
    X_train, X_test = data[train_index], data[test_index]
    y_train, y_test = labels[train_index], labels[test_index]

    # สร้างและฝึกโมเดล
    model = RandomForestClassifier(n_estimators=100, criterion="entropy", max_depth=30, min_samples_split=5)
    model.fit(X_train, y_train)

    # ทำนายผลและคำนวณความแม่นยำ
    y_pred = model.predict(X_test)
    score = accuracy_score(y_test, y_pred)
    accuracy_scores.append(score)

    print(f'Fold accuracy: {score * 100:.2f}%')

# คำนวณค่าเฉลี่ยของความแม่นยำจากทุก fold
average_accuracy = np.mean(accuracy_scores)
print(f'Average Accuracy from {k}-fold Cross Validation: {average_accuracy * 100:.2f}%')

# บันทึกโมเดลที่ฝึกเสร็จแล้ว
f = open('model_best.p', 'wb')
pickle.dump({'model': model}, f)
f.close()