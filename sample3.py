import re

# Define the regex patterns
regex_filter = {
    'm3': '.*m[34]',
    'm5': '.*5',
    'm7': '.*m7'
}

# Define a function to apply the regex filters and sum the values
def apply_regex_filter(data):
    result = {}
    for key in data:
        temp = {}
        for regex_key, regex_pattern in regex_filter.items():
            temp[regex_key] = sum([value for sub_key, value in data[key].items() if re.match(regex_pattern, sub_key)])
        result[key] = temp
    return result

# Apply the regex filters to the input data
input_data = {
    'us': {'bank1m7': 9.0, 'bank401m5': 10.0, 'bank501m5': 15.0, 'bank401m4': 10, 'bank301m3': 11},
    'test': {'bank1m7': 10.0, 'bank401m5': 11.0, 'bank501m5': 12.0, 'bank401m4': 13, 'bank301m3': 14}
}
output_data = apply_regex_filter(input_data)

# Print the output data
print(output_data)
