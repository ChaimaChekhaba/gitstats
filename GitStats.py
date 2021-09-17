import io
import subprocess
import os
import re
import pandas


# commit dataframe columns
commits_columns = ['commit_hash_key', 'Author', 'Date', 'Comment']

# tag dataframe columns
tags_columns = ['tag', '#contributors', '#release_date', '#loc', '#cloc', '#files', '#xml_files', '#java_files',
                '#added_files', '#changed_files', '#renamed_files', '#deleted_files', '#unchanged_files',
                '#added_xml_files', '#changed_xml_files', '#renamed_xml_files', '#deleted_xml_files',
                '#unchanged_xml_files', '#added_java_files', '#changed_java_files', '#renamed_java_files',
                '#deleted_java_files', '#unchanged_java_files']


# compute the number of code of lines changed from the result of git diff
def get_cloc(awk_result):
    data = io.StringIO(awk_result)
    df = pandas.read_csv(data, sep="\t", names=['added', 'removed', 'file'])
    return df['added'].sum(), df['removed'].sum()


class GitStats:
    def __init__(self, repo_name, result_file):
        # repo_name: the git repo to analyze
        self.repo_name = repo_name
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
        r = subprocess.getoutput('git tag')
        tags = re.split('\n', r)
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
            nb_release_date = subprocess.getoutput(f'git show -s --format=%ci {sha2}')
            if i == 0:  # the first tag, we need to use the first commit in the repo
                sha1 = self.df_commits.iloc[[-1], [0]].values.tolist()[0][0]
                first_commit = sha1

            nb_added_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^A" | wc -l ')
            nb_changed_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^C" | wc -l ')
            nb_renamed_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^R" | wc -l ')
            nb_deleted_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^D" | wc -l ')
            nb_unchanged_files = subprocess.getoutput(f'git diff --name-only {sha1}..{sha2} >> changed.txt &&'
                                                      f' git ls-files >> all.txt &&'
                                                      f' comm --nocheck-order -23 all.txt changed.txt >> unchanged.txt'
                                                      f' &&  wc -l < unchanged.txt')
            subprocess.getstatusoutput(f'rm -f all.txt changed.txt unchanged.txt')
            nb_added_xml_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^A" | '
                                                      f'grep ".xml" | wc -l ')
            nb_changed_xml_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^C" | '
                                                        f'grep ".xml" | wc -l ')
            nb_renamed_xml_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^R" |'
                                                        f'grep ".xml" | wc -l ')
            nb_deleted_xml_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^D" | '
                                                        f'grep ".xml" | wc -l ')
            nb_unchanged_xml_files = subprocess.getoutput(f'git diff --name-only {sha1}..{sha2} >> changed.txt &&'
                                                          f' git ls-files >> all.txt && comm --nocheck-order '
                                                          f'-23 all.txt changed.txt >> unchanged.txt'
                                                          f' && grep ".xml" unchanged.txt | wc -l')
            subprocess.getstatusoutput(f'rm -f all.txt changed.txt unchanged.txt')
            nb_added_java_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^A" | '
                                                       f'grep ".java" | grep -v "Test.java" | wc -l ')
            nb_changed_java_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^C" | '
                                                         f'grep ".java" | grep -v "Test.java" | wc -l ')
            nb_renamed_java_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^R" |'
                                                         f'grep ".java" | grep -v "Test.java" | wc -l ')
            nb_deleted_java_files = subprocess.getoutput(f'git diff --name-status {sha1}..{sha2} | grep "^D" | '
                                                         f'grep ".java" | grep -v "Test.java" | wc -l ')
            nb_unchanged_java_files = subprocess.getoutput(f'git diff --name-only {sha1}..{sha2} >> changed.txt &&'
                                                           f' git ls-files >> all.txt && comm --nocheck-order '
                                                           f'-23 all.txt changed.txt >> unchanged.txt && '
                                                           f' grep ".java" unchanged.txt | grep -v "Test.java" | wc -l')
            subprocess.getstatusoutput(f'rm -f all.txt changed.txt unchanged.txt')
            nb_contributors = subprocess.getoutput(f'git log --pretty=format:"%an" {sha1}..{sha2}| sort | uniq | wc -l')
            changed_files = subprocess.getoutput(f'git log --numstat --pretty=\"%H\" {sha1}..{sha2} | grep ".java" '
                                                 f'| grep -v "Test.java"')
            # point the head of the git log on the sha2 commit to retore the state of all the files
            subprocess.getstatusoutput(f'git reset --hard {sha2}')
            nb_loc = subprocess.getoutput(f'git ls-files | grep ".java" | grep -v "Test.java" | xargs cat | wc -l')
            # redo the reset of the repo to point to the last commit
            subprocess.getstatusoutput(f'git reset --hard {first_commit}')
            nb_cloc = get_cloc(changed_files)
            sha1 = sha2
            i += 1
            data.append([tag, nb_contributors, nb_release_date, nb_loc, nb_cloc, nb_files, nb_xml_files, nb_java_files,
                         nb_added_files, nb_changed_files, nb_renamed_files, nb_deleted_files, nb_unchanged_files,
                         nb_added_xml_files, nb_changed_xml_files, nb_renamed_xml_files, nb_deleted_xml_files,
                         nb_unchanged_xml_files, nb_added_java_files, nb_changed_java_files, nb_renamed_java_files,
                         nb_deleted_java_files, nb_unchanged_java_files])
        self.df_tags = pandas.DataFrame(data, columns=tags_columns)
        self.df_tags.to_csv(f'{self.repo_name}-gitstat.csv', index=False)
