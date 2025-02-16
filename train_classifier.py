import pickle

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from collections import Counter


data_dict = pickle.load(open('./data.pickle', 'rb'))

data = np.asarray(data_dict['data'])
labels = np.asarray(data_dict['labels'])

# ตรวจสอบจำนวนตัวอย่างในแต่ละคลาส
class_counts = Counter(labels)
print("จำนวนตัวอย่างในแต่ละแบบ:", class_counts)

x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

model = RandomForestClassifier(n_estimators=100, max_depth=10)

model.fit(x_train, y_train)

y_predict = model.predict(x_test)

score = accuracy_score(y_predict, y_test)

print('{}% of samples were classified correctly !'.format(score * 100))
print("Model use:", model)

f = open('model.p', 'wb')
pickle.dump({'model': model}, f)
f.close()
