def calculate_checksum(numbers):
    accumulated_sum, multiplier = 0, 3
    for number in reversed(numbers):
        accumulated_sum += int(number) * multiplier
        multiplier = 1 if multiplier == 3 else 3
    return accumulated_sum

def is_valid_jan_code(jan_code_str):
    if len(jan_code_str) not in [8, 13]:
        return False  # JANコードは8桁または13桁である必要があります
    numbers = list(jan_code_str[:-1])
    expected_cd = calculate_checksum(numbers) % 10
    expected_cd = 10 - expected_cd if expected_cd != 0 else 0
    actual_cd = int(jan_code_str[-1])
    return expected_cd == actual_cd


def is_valid_tax(tax_num):
    return tax_num in [0, 8, 10]
