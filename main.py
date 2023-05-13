import os
import subprocess
import argparse


parser = argparse.ArgumentParser(description='Print the contents of a .git directory.')
parser.add_argument('path', metavar='path', type=str, nargs='?', default='.git', help='path to the .git directory')
parser.add_argument('-i', '--ignore', metavar='ignore', type=str, nargs='?', default='hooks', help='comma-separated list of files to ignore')
parser.add_argument('--cleartext-index', action='store_true', help='print the index file in cleartext using git ls-files --staged instead of printing the raw binary file')
args = parser.parse_args()


def print_tree(dir_path, prefix=''):
    entries = os.scandir(dir_path)
    entries = sorted(entries, key=lambda e: e.is_file())
    entries = sorted(entries, key=lambda e: e.name)
    for i, entry in enumerate(entries):
        if entry.name in args.ignore.split(','):
            continue

        if i == len(entries) - 1:
            print(prefix + '└──', end='')
            new_prefix = prefix + '   '
        else:
            print(prefix + '├──', end='')
            new_prefix = prefix + '│  '
        if entry.is_file():
            print(entry.name)
            is_git_object = len(entry.name) == 38
            is_git_index = entry.name == 'index'
            if is_git_object:
                hash = entry.path.split('/')[-2] + entry.name
                lines = subprocess.check_output(['git', 'cat-file', '-p', hash]).decode("UTF-8", "ignore").split('\n')
            elif is_git_index and args.cleartext_index:
                lines = subprocess.check_output(['git', 'ls-files', '--stage']).decode("UTF-8", "ignore").split('\n')
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


print_tree(args.path)
