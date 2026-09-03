# Sam Pirkl and Soren Patel
# solution2.py

"""
pseudocode:
1. make dict
2. open file and loop through lines in file
3. for each line, get the words and make them lowercase and stripped
4. increment the word count for each word in line
5. sort the values in the dict in decreasing order
6. print the top 5 results
"""

# create the dictionary to hold the word counts 
word_freq_dict = {}

# open the file
with open("words.txt", "r") as file:
    
    for line in file:
        # get the words from each line
        words = line.split()
        
        # loop through words from each line
        for raw_word in words:
            # make it lowercase and remove unnecessary chars
            word = raw_word.lower().strip()

            # get the count from the dict, if it doesnt exist make it 0. always add 1
            word_freq_dict[word] = word_freq_dict.get(word, 0) + 1

# sort the dict based on values, GOT THIS FROM GOOGLE AI
sorted_dict = sorted(word_freq_dict.items(), key=lambda item: item[1], reverse=True)
    
# print the top five word counts
for word, count in sorted_dict[:5]:
    print(f"{word}: {count}")
    