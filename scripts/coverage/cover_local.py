import os
import re

print("WARNING: This script is desctructive. Please make sure that you stage all changes in the repository before running this, and discard any new changes after the script terminates and you record the coverage.")
input("Press Enter to continue...")

def remove_comments(code):
    # Remove all sequences of triple quotes from the code
    pattern = re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'')
    code = pattern.sub('', code)

    # Remove all lines that start with #
    lines = [l for l in code.split('\n') if l.strip() != '']
    lines = [line for line in lines if not line.strip().startswith('#')]
    code = '\n'.join(lines)

    return code, len(lines)

python_path = "./../commons-cli-translated/src/main/python"

# get list of all files in directory {python_path}
files = [f for f in os.listdir(python_path) if f.endswith('.py')]

full_loc = {}

# open each file and read contents
for file in files:
    if file == 'java_handler.py':
        # Leave as it is        
        continue

    with open(f"{python_path}/{file}") as f:
        content, num_lines = remove_comments(f.read())

    full_loc[file.split('.')[0]] = num_lines

    # add logger to each file
    content = f"""
import sys
def trace_calls(frame, event, arg):
    with open('trace.txt', 'a') as f:
        f.write(f"{{frame.f_code.co_filename.split('/')[-1].split('.')[0]}}: {{frame.f_lineno}}\\n")
    return trace_calls
sys.settrace(trace_calls)
{content}
"""

    if not content.endswith('\n'):
        content += '\n'

    with open(f"{python_path}/{file}", 'w') as f:
        f.write(content)

os.system('mvn test -Drat.skip > /dev/null 2>&1')

with open('trace.txt') as f:
    lines = f.readlines()

loc = {}

for line in lines:
    cls, line_no = line.strip().split(': ')
    line_no = int(line_no)

    if cls != 'java_handler':
        if cls not in loc:
            loc[cls] = set()

        if line_no > 7:
            loc[cls].add(line_no)


data = [["File", "LOC", "LOC covered", "LOC covered %"]]

for file, num_lines in full_loc.items():
    if file == 'java_handler.py':
        continue

    if file in loc and num_lines > 0:
        covered = len(loc[file])
        data.append([file, num_lines, covered, f"{covered / num_lines * 100:.2f}"])
    else:
        data.append([file, num_lines, 0, 0])


# Calculate the maximum width of each column
col_widths = [max(len(str(row[i])) for row in data) for i in range(len(data[0]))]
col_widths[1] = 4

# Print the table separator
print("-" * (sum(col_widths) + 3 * (len(data[0]) - 1)))

# Print the table headers
print(" | ".join("{:<{}}".format(header, col_widths[i]) for i, header in enumerate(data[0])))

# Print the table separator
print("-" * (sum(col_widths) + 3 * (len(data[0]) - 1)))

# Print the table rows
for row in data[1:]:
    print(" | ".join("{:<{}}".format(str(cell), col_widths[i]) for i, cell in enumerate(row)))

# Add a row with totals
total_full_loc = sum([row[1] for row in data[1:]])
total_loc = sum([row[2] for row in data[1:]])
totals = ["Total", total_full_loc, total_loc, f"{total_loc / total_full_loc * 100:.2f}"]
data.append(totals)

# Print the table separator
print("-" * (sum(col_widths) + 3 * (len(data[0]) - 1)))

# Print the totals row
print(" | ".join("{:<{}}".format(str(cell), col_widths[i]) for i, cell in enumerate(totals)))
