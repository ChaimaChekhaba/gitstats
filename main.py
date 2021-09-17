# This is a sample Python script.
from GitStats import GitStats
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def run(repo_name):
    # Use a breakpoint in the code line below to debug your script.
    GitStats(repo_name).compute_stats()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run('/home/chaima/Phd/JournalPaper/QualitativeStudy/apps-done/ThirtyInch')
