def generate_ngrams(text, n):
    # Split the text into words
    words = text.split()
    ngrams = []
    # Generate n-grams
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)

    return ngrams

# Take inputs
n = int(input("Enter the number of grams (e.g., 1 for unigram, 2 for bigram, etc.): "))
text = "Enter the number of grams (e.g., 1 for unigram, 2 for bigram, etc.): "

# Generate n-grams
ngrams = generate_ngrams(text, n)

# Display the n-grams
print(f"\n{n}-grams:")

for gram in ngrams:
    print(gram)
