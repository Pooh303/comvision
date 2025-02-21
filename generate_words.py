import itertools
import nltk
from nltk.corpus import words as nltk_words
from nltk.corpus import brown
import string

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

try:
    nltk.data.find('corpora/brown')
except LookupError:
    nltk.download('brown')


def generate_lba_words(max_length, use_brown_corpus=False):
    """
    Generates all possible words up to max_length using A-Z and filters real words.

    Args:
        max_length (int): Maximum length of generated words.
        use_brown_corpus (bool): Whether to use the Brown corpus for filtering.

    Returns:
        list: Sorted list of valid English words found.
    """
    letters = string.ascii_uppercase  # A-Z
    english_words = set(word.lower() for word in (brown.words() if use_brown_corpus else nltk_words.words()))

    real_words = sorted(
       word for length in range(1, max_length + 1)
        for comb in itertools.product(letters, repeat=length)
        if (word := "".join(comb).lower()) in english_words
    )

    return real_words


def create_words_file(max_length, filename="words.txt", use_brown=False):
    """
    Generates words up to a specified length and writes the real words to a file.

    Args:
        max_length: The maximum length of the words.
        filename: The name of the file to create.
        use_brown: Whether to use the Brown corpus (larger, slower).
    """
    real_words = generate_lba_words(max_length, use_brown_corpus=use_brown)
    with open(filename, "w") as f:
        f.writelines(f"{word}\n" for word in real_words)

    print(f"{filename} file created with {len(real_words)} words.")


# Example Usage:
# words_length_3 = generate_lba_words(3)
# print(f"Real words up to length 3: {words_length_3}")

# words_length_4 = generate_lba_words(4)
# print(f"Real words up to length 4: {words_length_4}")

# words_length_4_brown = generate_lba_words(4, use_brown_corpus=True)
# print(f"Real words up to length 4 (Brown corpus): {words_length_4_brown}")

# Create words files
create_words_file(4, use_brown=True, filename="words.txt")  # Generate up to length 4 with Brown corpus.
# create_words_file(4, filename="words_nltk_4.txt", use_brown=False)  # Generate up to length 4, without Brown corpus.
# create_words_file(5, use_brown=True, filename="words_brown_5.txt")
# create_words_file(5, filename="words_nltk_5.txt", use_brown=False)