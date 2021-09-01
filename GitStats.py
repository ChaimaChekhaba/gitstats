import subprocess
import os
import re
import pandas

# TODO
# Adding the number of xml and all files added updated, renamed and removed

# commit dataframe columns
commits_columns = ['commit_hash_key', 'Author', 'Date', 'Comment']

# tag dataframe columns
tags_columns = ['tag', '#contributors', '#release_date', '#loc', '#cloc',  '#files', '#xml_files', '#java_files',
                '#added_xml_files', '#unchanged_xml_files', '#changed_xml_files', '#added_xml_files',
                '#removed_xml_files', '#renamed_xml_files', '#unchanged_java_files', '#changed_java_files',
                '#added_java_files', '#removed_java_files', '#renamed_java_files']


class GitStats:
    def __init__(self, repo_name, result_file):
        # repo_name: the git repo to analyze
        self.repo_name = repo_name
        # result_file: the csv file to store the results
        self.result_file = result_file
        # dataframe of commits
        self.df_commits = []
        # dataframe_tags
        self.df_tags = []

    def compute_stats(self):
        os.chdir(self.repo_name)
        r = subprocess.getoutput('git log')
        commits = re.split('(commit [0-9a-zA-Z]+)', r)
        data, row, i = [], [], 0
        for commit in commits:
            if len(commit) != 0:
                if i == 0:  # the first part of the commit
                    first_part = commit.split('commit ')[1]
                    row.append(first_part)
                    i = 1
                else:  # i == 1
                    commit_info = commit.split('\n')
                    author, date, comment = None, None, None
                    while '' in commit_info:
                        commit_info.remove('')

                    for info in commit_info:
                        if info.__contains__('Author'):
                            author = info.split('Author:')[1]
                        else:
                            if info.__contains__('Date'):
                                date = info.split('Date:')[1]
                            else:
                                comment = info

                    row.append(author)
                    row.append(date)
                    row.append(comment)
                    i = 0
                    data.append(row)
                    row = []

        self.df_commits = pandas.DataFrame(data, columns=commits_columns)
        print(f'commits {self.df_commits}')
        r = subprocess.getoutput('git tag')
        tags = re.split('\n', r)
        print(tags)
        data = []
        i = 0
        for tag in tags:
            # get the commit which a tag is pointing to
            sha2 = subprocess.getoutput(f'git rev-list -n 1 {tag}')
            nb_files = subprocess.getoutput(f'git ls-tree --name-status -r {sha2} | wc -l')
            nb_xml_files = subprocess.getoutput(f'git ls-tree --name-status -r {sha2} '
                                                f'| grep "/res/layout" | grep ".xml" | wc -l')
            nb_java_files = subprocess.getoutput(f'git ls-tree --name-status -r {sha2} '
                                                 f'| grep ".java" | grep -v "Test.java" | wc -l')
            nb_contributors = 0
            nb_release_date = 0
            nb_loc = 0
            nb_cloc = 0
            if i == 0:  # the first tag, we need to use the first commit in the repo
                sha1 = self.df_commits.iloc[[-1], [0]].values.tolist()[0][0]

            nb_added_files = subprocess.getoutput(f'git diff --name-status {sha1} {sha2} | grep "^A" | wc -l ')
            print(f'{sha1} {sha2} added files {nb_added_files} nb_files in the repo at this commit {nb_java_files}')
            sha1 = sha2
            i += 1
            data.append([tag, nb_contributors, nb_release_date, nb_loc, nb_cloc, nb_files, nb_xml_files, nb_java_files,
                         ])

            # ['tag', '#classes', '#contributors', '#release_date', '#loc', '#cloc', '#unchanged_classes',
            # '#changed_classes', '#added_classes', '#removed_classes', '#renamed_classes']
        # self.df_tags = pandas.DataFrame(data, columns=tags_columns)
        # to compute the difference between two releases
