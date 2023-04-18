import re

input_data = {
    'us': {
        'bank1m7': 9.0,
        'bank401m5': 10.0,
        'bank501m5': 15.0,
        'bank401m4': 10,
        'bank301m3': 11
    },
    'test': {
        'bank1m7': 10.0,
        'bank401m5': 11.0,
        'bank501m5': 12.0,
        'bank401m4': 13,
        'bank301m3': 14
    }
}

regex_filter = {
    'm3': '.*m[34]',
    'm5': '.*5',
    'm7': '.*m7'
}

output_data = {}

for country, banks in input_data.items():
    output_data[country] = {}
    for bank, value in banks.items():
        for m_value, regex_pattern in regex_filter.items():
            if re.match(regex_pattern, bank):
                output_data[country][m_value] = output_data[country].get(m_value, 0) + value
                break  # stop looking at other regex patterns once a match is found
    
    m3_value = output_data[country].get('m3', 0)
    m5_value = output_data[country].get('m5', 0)
    if m3_value and m5_value:
        pct_diff = abs(m3_value - m5_value) / ((m3_value + m5_value) / 2) * 100
        output_data[country]['pct_diff'] = pct_diff

print(output_data)
