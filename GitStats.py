

class GitStats:
    def __init__(self, repo_name, result_file):
        # repo_name: the git repo to analyze
        self.repo_name = repo_name
        # reuslt_file: the csv file to store the results
        self.result_file = result_file

    def compute_stats(self):
        print()