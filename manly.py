import sys
import subprocess
import re


def flag_parser(raw_flags):
    '''Splits concatenated flags (eg. ls' "-la") in to individual flags
    (eg. "-la" -> "-l", -"a".).

    Args:
        raw_flags (list): The flags as they would be given normally.

    Returns:
        flags (list): The disassembled concatenations of flags, and regular
            verbose flags as given.'''
    flags = []
    for flag in raw_flags:
        if flag.startswith('-'):
            if not flag.startswith('--'):
                flag = flag.replace('-', '')
                for char in flag:
                    flags.append('-' + char)
            else:
                flags.append(flag)
        else:
            pass
    return flags


def parse_manpage(page, args):
    '''Scan the manpage for blocks of text, and check if the found blocks
    have sections that match the general manpage-flag descriptor style.

    Args:
        page (str): The utf-8 encoded manpage.
        args (iter): An iterable of flags passed to check against.

    Returns:
        output (list): The blocks of the manpage that match the given flags.'''
    sections = []
    temp_sections = []
    output = []

    for line in page.split('\n'):
        line = line + '\n'
        if line != '\n':
            temp_sections.append(line)
        else:
            sections.append(''.join(temp_sections))
            temp_sections = []

    for section in sections:
        section_top = section.strip().split('\n')[:2]
        first_line = section_top[0].split(',')

        for arg in args:
            try:
                if any(seg.strip().startswith(arg) for seg in first_line) \
                  or section_top[1].strip().startswith(arg):
                    output.append(section.rstrip())
                    break
            except IndexError:
                pass
    return output


def main():
    command = sys.argv[1]
    flags = flag_parser(sys.argv[2:])
    manpage = subprocess.check_output(['man', command]).decode('utf-8')

    title = re.search(r'(?<=^NAME\n\s{7}).+', manpage, re.MULTILINE).group(0)

    output = parse_manpage(manpage, flags)

    print('\nSearching for:', command, *flags, '\n')
    if output:
        print(title)
        print('-' * len(title))
        for flag in output:
            print(flag)
    else:
        print('No flags found.')
    print()


if __name__ == '__main__':
    main()
