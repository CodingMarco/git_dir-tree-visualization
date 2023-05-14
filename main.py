import os
import subprocess
import argparse


class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    ORANGE = '\033[33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


parser = argparse.ArgumentParser(description='Print the contents of a .git directory.')
parser.add_argument('path', metavar='path', type=str, nargs='?', default='.git', help='path to the .git directory')
parser.add_argument('-i', '--ignore', metavar='ignore', type=str, nargs='?', default='hooks', help='comma-separated list of files to ignore')
parser.add_argument('--cleartext-index', action='store_true', help='print the index file in cleartext using git ls-files --staged instead of printing the raw binary file')
args = parser.parse_args()


def is_likely_blob(lines):
    return not any(line.startswith('tree ') or line.startswith('parent ') or line.startswith('author ')
                    or line.startswith('committer ') or line.startswith('encoding ') or line.startswith('gpgsig ')
                    or line.startswith('mergetag ') or line.startswith('object ') or line.startswith('type ')
                    or line.startswith('tag ') or line.startswith('tagger ') or " blob " in line or " tree " in line for line in lines)


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
            print(colors.BOLD + colors.GREEN + entry.name + colors.ENDC)
            is_git_object = len(entry.name) == 38
            is_git_index = entry.name == 'index'
            likely_blob = False
            if is_git_object:
                hash = entry.path.split('/')[-2] + entry.name
                lines = subprocess.check_output(['git', 'cat-file', '-p', hash]).decode("UTF-8", "ignore").split('\n')
                likely_blob = is_likely_blob(lines)
            elif is_git_index and args.cleartext_index:
                lines = subprocess.check_output(['git', 'ls-files', '--stage']).decode("UTF-8", "ignore").split('\n')
            else:
                with open(entry.path, 'rb') as f:
                    lines = f.read().decode("UTF-8", "ignore").split('\n')

            # Split lines longer than 80 characters into multiple lines ending with \
            max_len = 820
            for i, line in enumerate(lines):
                if len(line) > max_len:
                    lines[i] = line[:max_len] + '\\'
                    lines.insert(i + 1, line[max_len:])

            color = colors.CYAN if likely_blob else colors.ORANGE

            for line in lines:
                print(new_prefix + color + line.strip() + colors.ENDC)
        else:
            print(entry.name + '/')
            print_tree(entry.path, new_prefix)


print_tree(args.path)
