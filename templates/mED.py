def levenshtein_distance(word1, word2):
    m, n = len(word1), len(word2)
    
    # Create a matrix to store distances
    dp = [[0 for _ in range(n+1)] for _ in range(m+1)]
    
    # Initialize the matrix
    for i in range(m+1):
        dp[i][0] = i  # Cost of deletions
    for j in range(n+1):
        dp[0][j] = j  # Cost of insertions
    
    # Populate the matrix with minimum edit distances
    for i in range(1, m+1):
        for j in range(1, n+1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No change needed
            else:
                dp[i][j] = 1 + min(dp[i-1][j],    # Deletion
                                   dp[i][j-1],    # Insertion
                                   dp[i-1][j-1])  # Substitution
    
    return dp[m][n]

# Function to correct the spelling
def spell_correct(misspelled_word, correct_words):
    # Initialize variables to track the closest match
    min_distance = float('inf')
    closest_word = None
    
    # Compare the misspelled word with each correct word
    for word in correct_words:
        distance = levenshtein_distance(misspelled_word, word)
        if distance < min_distance:
            min_distance = distance
            closest_word = word
    
    return closest_word, min_distance

# Test the spell correction
misspelled_word = input("Enter the misspelled word: ")
correct_words = ["jackal", "joker", "anchor", "baker", "backdoor", "tractor"]

corrected_word, distance = spell_correct(misspelled_word, correct_words)
print(f"\nOriginal word: {misspelled_word}")
print(f"Suggested correction: {corrected_word}")
print(f"Edit Distance: {distance}")
