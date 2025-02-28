import string

letters = string.ascii_uppercase.replace('J', '').replace('Z', '')
labels_dict = {i: letter for i, letter in enumerate(letters)}

print(labels_dict)