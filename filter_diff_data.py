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


sorted_data = {}
for key, value in input_data.items():
    sorted_data[key] = {}
    m35_data = {}
    for m_key in ['m3', 'm5']:
        if m_key in value.keys():
            m35_data.update(value[m_key])
    sorted_m35_data = dict(sorted(m35_data.items(), key=lambda item: item[1], reverse=True))
    sorted_data[key]['m35'] = {}
    sorted_data[key]['m35'].update(sorted_m35_data)
    sorted_data[key]['m35']['percentage_diffs'] = []
    first_val = list(sorted_m35_data.values())[0]
    for k, v in sorted_m35_data.items():
        if k != list(sorted_m35_data.keys())[0]:
            percentage_diff = abs((v - first_val) / first_val * 100)
            print(percentage_diff)
            sorted_data[key]['m35']['percentage_diffs'].append(percentage_diff)
    if all(abs(diff) >= 10 for diff in sorted_data[key]['m35']['percentage_diffs']):
        print(list(sorted_m35_data.keys())[0])
#     return None
# print(get_first_element_with_10_percent_diff(input_data))
