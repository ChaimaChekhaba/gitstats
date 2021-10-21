from GitStats import GitStats
import argparse
import os
import sys
# TO-DO: i should add the special case when the app does not have any tags at all
# TO-DO: i should also change the path name of the app to the git url


def run(repo_name):
    return GitStats(repo_name).compute_stats()


if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(description='compute statistics on Git repo')

    my_parser.add_argument('Path',
                           metavar='path',
                           type=str,
                           help='the path to the git repo')

    args = my_parser.parse_args()

    input_path = args.Path

    if not os.path.isdir(input_path):
        print('The path specified does not exist')
        sys.exit()

    result = run(input_path)
    print(f'Result in {result}')
