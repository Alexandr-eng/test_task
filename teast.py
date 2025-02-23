def generate_sequence(n):
    sequence = []
    current_number = 1
    while len(sequence) < n:

        sequence.extend([current_number] * current_number)
        current_number += 1
    return sequence[:n]


n = int(input("Введите количество элементов последовательности: "))


result = generate_sequence(n)
print("Последовательность:", result)