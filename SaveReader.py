import random
import re
import csv
import os
import time
from datetime import datetime


def read_save(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    file.close()
    # splits the file into relevant databases
    # the order of databases, though not in a form readable by a computer, can be seen in the file "databases_order.txt"
    return content.split('database')


# Per previous experiments, the relevant data - pop data - is the second part of the save file
def get_pops_data(content):
    return content[1]


# Will stop working after the year 9999, this year is impossible in this context
# Generally returns year if in the first half and year.5 if in the second
def get_game_year(content):
    game_data = content[0]
    year = 0.0
    for line in game_data.split('\n'):
        line = line.strip()
        if line.startswith('game_date='):
            date = datetime.strptime(line.split('game_date=')[1], '%Y.%m.%d')
            year = float(date.year) if date.month < 7 else float(date.year) + 0.5
    return year


# As much as I would have loved to make this a function with regular expressions, no regular expression
# I made seemed to work
def parse_pop_data(file_name, output_file):
    file_parts = read_save(file_name)
    file_content = get_pops_data(file_parts)
    pop_data = {}

    # Split the content by lines
    lines = file_content.split('\n')

    # Get the year of the game
    year = get_game_year(file_parts)

    expected_tags = ['year', 'workforce', 'dependents', 'wealth', 'loyalists_and_radicals', 'literacy',
                     'job_satisfaction', 'profession', 'is_discriminated']

    pop_number = None
    inside_block = False

    for line in lines:
        line = line.strip()

        if re.match(r'^\d+=\{', line):
            # Start of a new block
            pop_number = int(line.split('=')[0])
            pop_data[pop_number] = {}
            pop_data[pop_number]['year'] = f'{year}'
            inside_block = True
        elif inside_block and line == '}':
            # End of a block
            pop_number = None
            inside_block = False
        elif inside_block and line.startswith('workforce='):
            # Extract population size part 1
            workforce = int(line.split('=')[1])
            pop_data[pop_number]['workforce'] = workforce
        elif inside_block and line.startswith('dependents'):
            # Extract population size part 2
            dependents = int(line.split('=')[1])
            pop_data[pop_number]['dependents'] = dependents
        elif inside_block and line.startswith('wealth='):
            # Extract wealth
            wealth = float(line.split('=')[1])
            pop_data[pop_number]['wealth'] = wealth
        elif inside_block and line.startswith('loyalists_and_radicals='):
            # Extract loyalists_and_radicals
            loyalists_and_radicals = float(line.split('=')[1])
            pop_data[pop_number]['loyalists_and_radicals'] = loyalists_and_radicals
        elif inside_block and line.startswith('num_literate'):
            # Extract literacy rate
            literacy = float(line.split('=')[1])
            pop_data[pop_number]['literacy'] = literacy
        elif inside_block and line.startswith('job_satisfaction'):
            # Extract job satisfaction
            job_satisfaction = float(line.split('=')[1])
            pop_data[pop_number]['job_satisfaction'] = job_satisfaction
        elif inside_block and line.startswith('type'):
            # Extract profession, necessary for calculating class
            profession = line.split('=')[1]
            pop_data[pop_number]['profession'] = profession
        elif inside_block and line.startswith('is_discriminated'):
            discriminated = 1 if line.split('=')[1] == 'yes' else 0
            pop_data[pop_number]['is_discriminated'] = discriminated
        elif not inside_block and '=' in line:
            # Ignore n=none lines
            continue

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(expected_tags)
        for pop in pop_data:
            entry = [year]
            if 'profession' not in pop_data[pop]:
                pop_data[pop]['profession'] = 'none'
            if 'is_discriminated' not in pop_data[pop]:
                pop_data[pop]['is_discriminated'] = 0
            for tag in expected_tags[1:]:
                if tag not in pop_data[pop]:
                    pop_data[pop][tag] = 0
                entry.append(pop_data[pop][tag])
            writer.writerow(entry)
    file.close()
    return pop_data


def write_to_csv(pop_data, output_file):
    with (open(output_file, mode='w', newline='') as file):
        writer = csv.writer(file)
        keys = pop_data.keys()
        writer.writerow(keys)
        # Write the data
        for pop_number, data in pop_data.items():
            writer.writerow([data.get(key, 0) for key in keys])


def process_files(input_dir, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all files in the input directory
    files = os.listdir(input_dir)

    for file_name in files:
        input_file_path = os.path.join(input_dir, file_name)
        output_file_path = os.path.join(output_dir, f'{os.path.splitext(file_name)[0]}.csv')

        # Parse data
        parse_pop_data(input_file_path, output_file_path)

        print(f'File "{file_name}" processed and saved as "{output_file_path}"')


def summarize_csv_files(input_folder, output_csv_filename):
    combined_data = []
    header_written = False

    # Iterate over all CSV files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)

            with open(file_path, mode='r', newline='') as file:
                reader = csv.reader(file)
                header = next(reader)  # Read the header
                print(f"processing file {file_path}")
                # If the header hasn't been written to the combined data, write it once
                if not header_written:
                    combined_data.append(header)
                    header_written = True

                # Append the data rows
                for row in reader:
                    if row[1] != '0':
                        combined_data.append(row)
            file.close()
    # Write the combined data to the output CSV file
    with open(output_csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in combined_data:
            writer.writerow(row)
    file.close()


# Choosing n random elements from csv
# It could be way quicker to choose random elements while processing files, before summarization, but this
# Allows easier access to entries and simplifies choosing of entries, and I was not limited by computing capability
def choose_random_entries(input_file, n):
    random_data = []
    if input_file.endswith('.csv'):
        with open(input_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            random_data.append(header)
            data = list(reader)
            sample = random.sample(data, n)

        with open(f'cut_{input_file}_{n}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for row in sample:
                writer.writerow(row)

    else:
        raise NameError('Please provide a valid CSV file')
