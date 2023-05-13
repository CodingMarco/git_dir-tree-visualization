import os
import subprocess

def print_tree(dir_path, prefix=''):
    entries = os.scandir(dir_path)
    entries = sorted(entries, key=lambda e: e.is_file())
    entries = sorted(entries, key=lambda e: e.name)
    for i, entry in enumerate(entries):
        if i == len(entries) - 1:
            print(prefix + '└──', end='')
            new_prefix = prefix + '   '
        else:
            print(prefix + '├──', end='')
            new_prefix = prefix + '│  '
        if entry.is_file():
            print(entry.name)
            # Get the output of "git cat-file -p <hash>"
            # and print it with the new prefix
            if len(entry.name) == 38:
                hash = entry.path.split('/')[-2] + entry.name
                lines = subprocess.check_output(['git', 'cat-file', '-p', hash]).decode("UTF-8", "ignore").split('\n')
            else:
                with open(entry.path, 'rb') as f:
                    lines = f.read().decode("UTF-8", "ignore").split('\n')

            # Split lines longer than 80 characters into multiple lines ending with \
            max_len = 82
            for i, line in enumerate(lines):
                if len(line) > max_len:
                    lines[i] = line[:max_len] + '\\'
                    lines.insert(i + 1, line[max_len:])

            for line in lines:
                print(new_prefix + line.strip())
        else:
            print(entry.name + '/')
            print_tree(entry.path, new_prefix)

print_tree('.git')
