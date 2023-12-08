import datetime
import time
import click

from github import Github
from github.GithubException import RateLimitExceededException
from tqdm import tqdm

number_of_items = 1000
min_stars_count = 100
search_key_word = "partial( NOT is:fork language:Python"


def search_github(auth: Github, keyword: list) -> list:
    """Search the GitHub API for repositories using an input keyword.

    Args:
        auth: A Github authenticate object.
        keyword: A keyword string.

    Returns:
        A nested list of GitHub repositories returned for a keyword. Each result list contains the repository name,
        url, and description.
    """

    print('Searching GitHub using keyword: {}'.format(keyword))

    # set-up query
    query = keyword
    results = auth.search_code(query)

    # print results
    print(f'Found {results.totalCount} repo(s)')

    results_list = []
    for index in tqdm(range(0, results.totalCount if number_of_items>results.totalCount else number_of_items)):
        try:
            repo = auth.get_repo(results[index].repository.id)
            if(repo.stargazers_count > min_stars_count):
                results_list.append([results[index].html_url, results[index].repository.full_name])
            #print(results[repo].html_url)
            time.sleep(2)
        except RateLimitExceededException:
            time.sleep(60)
            results_list.append([results[index].html_url, results[index].repository.full_name])

    return results_list


@click.command()
@click.option('--token', prompt='Please enter your GitHub Access Token')
def main(token: str) -> None:

    # initialize and authenticate GitHub API
    auth = Github(token)
    keywords = [search_key_word]

    # search a list of keywords
    search_list = [keyword.strip() for keyword in keywords.split(',')]

    # search repositories on GitHub
    github_results = dict()
    for key in search_list:
        github_results[key] = []
        github_results[key] += search_github(auth, key)
        if len(search_list) > 1: time.sleep(120)

    # write out results
    timestamp = datetime.datetime.now()
    formatted_date = timestamp.strftime('%d') + timestamp.strftime('%b') + timestamp.strftime('%Y')
    full_filename = 'GitHub_Search_Results_' + formatted_date + '.html'

    print('Writing search results to: {}'.format(full_filename))
    html_document = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Your Page Title</title>
        </head>
        <body>
            <ul>
        '''
    for key in tqdm(github_results.keys()):
            for item in github_results[key]:
                html_tag = f'<li><a href="{item[0]}">{item[1]}</a></li>'
                html_document += html_tag
    html_document += '''
            </ul>
        </body>
        </html>
        '''
    with open(full_filename, 'w') as f_out:
        f_out.write(html_document)
    f_out.close()


if __name__ == '__main__':
    main()