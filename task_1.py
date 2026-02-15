import random

# random.seed(22)                                           # for debugging purpose to generate stable random list
# create list of 100 random numbers from 0 to 1000
random_list = [random.randint(0, 1000) for _ in range(100)]
# sort list from min to max
sorted_list = []                                            # initialize empty sorted list

for number in random_list:                                  # call every number in random list
    for i in range(len(sorted_list)):                       # call every index in sorted list
        sorted_number = sorted_list[i]                      # initialize number from sorted list by index
        if number < sorted_number:                          # compare number from random list with number in sorted list
            sorted_list.insert(i, number)                   # add number to sorted list with proper index
            break                                           # break loop when condition met
    if number not in sorted_list:                           # add number from random list to sorted list if it was not
        sorted_list.append(number)                              # eligible for condition

# calculate average for even and odd numbers
even_numbers = []                                           # initialize empty list of even numbers
even_sum = 0                                                # initialize sum of even numbers
odd_numbers = []                                            # initialize empty list of odd numbers
odd_sum = 0                                                 # initialize sum of odd numbers
for number in sorted_list:                                  # call every number in sorted list
    rem = number % 2                                        # count remainder from division by 2
    if rem == 1:                                            # if number is odd
        odd_sum += number                                   # add odd number to odd sum
        odd_numbers.append(number)                          # add odd number to odd list to count list length
    else:                                                   # if number is even
        even_sum += number                                  # add even number to even sum
        even_numbers.append(number)                         # add even number to even list to count list length

even_avg = even_sum / len(even_numbers)                     # count average of even numbers
odd_avg = odd_sum / len(odd_numbers)                        # count average of odd numbers

if __name__ == '__main__':
    print(f'The average of even numbers is {even_avg:.4f}')
    print(f'The average of odd numbers is {odd_avg:.4f}')
