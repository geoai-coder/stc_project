def filter_lines(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        i,j = 0,0
        for line in infile:
            if "是下辖的一个类似乡级单位。" in line:
                parts = line.split("是")
                if len(parts) == 2:  # Check if there's more than one word before the comma
                    j+=1
                    continue
            if line[0] == '，':
                continue
            i+=1
            outfile.write(line)
        print(i,j)

input_file = 'filtered_output_select2.txt'
output_file = 'filtered_output_select3.txt'
filter_lines(input_file, output_file)
