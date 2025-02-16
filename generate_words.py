import itertools

def generate_lba_words(max_length):
    """
    Generates a list of words using only the letters 'L', 'B', and 'A'.

    Args:
        max_length: The maximum length of the generated words.

    Returns:
        A list of unique words (strings).
    """
    letters = ['L', 'B', 'A']
    all_words = set()  # Use a set to automatically handle uniqueness

    for length in range(1, max_length + 1):
        for combination in itertools.product(letters, repeat=length):
            all_words.add("".join(combination))

    return sorted(list(all_words))  # Convert back to a list and sort


# Example Usage:
words_length_3 = generate_lba_words(3)
print(f"Words up to length 3: {words_length_3}")

words_length_4 = generate_lba_words(4)
print(f"Words up to length 4: {words_length_4}")


# For your words.txt file:
words_for_file = generate_lba_words(4)  # Or whatever max_length you want

with open("words.txt", "w") as f:
    for word in words_for_file:
        f.write(word + "\n")

print("words.txt file created.")