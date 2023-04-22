import re

input_data = {
    'us': {
        'm7': {'bank1m7': 9.0},
        'm5': {'bank401m5': 1000.0, 'bank501m5': 15.0},
        'm3': {'bank401m4': 10, 'bank301m3': 11}
    },
    'test': {
        'm7': {'test1m7': 9.0},
        'm5': {'btest401m5': 100.0, 'btest501m5': 19.0},
        'm3': {'btest401m4': 10, 'btest301m3': 110}
    }
}

# Combine m3 and m5 data and sort by descending order of values
combined_data = {}
for key, value in input_data.items():
    combined_data[key] = {}
    combined_data[key]['m35'] = {k: v for d in (value['m3'], value['m5']) for k, v in d.items()}
    combined_data[key]['m35'] = dict(sorted(combined_data[key]['m35'].items(), key=lambda x: x[1], reverse=True))

# Calculate percentage differences for each key in the combined m3 and m5 data
for key, value in combined_data.items():
    first_key, first_val = list(value['m35'].items())[0]
    percentage_diffs = []
    for k, v in list(value['m35'].items())[1:]:
        percent_diff = abs(round((v - first_val) / first_val * 100, 2))
        if percent_diff > 5:
            print(f"Key '{first_key}' in '{key}' has a difference of more than 10% with '{k}': {percent_diff}%")
        percentage_diffs.append((k, percent_diff))
    combined_data[key]['m35']['percentage_diffs'] = percentage_diffs
    
    print("here is the result", first_key)

print(combined_data)
