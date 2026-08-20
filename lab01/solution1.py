# Sam Pirkl
# solution1.py

"""
pseudocode:
1. make list of integers
2. open file and read each float or int from each line
3. sort the numbers in increasing order
4. print the sorted numbers
"""

# make an list of floats
nums = []

# open the file and add each number to the list
with open("numbers.txt", "r") as file:
    for line in file:
        # append number as a float if there's a period in the number string, else append as int
        nums.append(float(line.strip())) if "." in line else nums.append(int(line.strip()))

# sort the numbers and then print them
sorted_nums = sorted(nums)
for num in sorted_nums:
    print(num)

