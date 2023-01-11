import csv
from github import Github
import time
from datetime import datetime
import os.path

def authenticate():
    """
    Authenticate to Github Enterprise Cloud X
    """
    return Github("access_token")

def get_organization_and_repos(g):
    """
    Get the organization and all the repositories for the organization
    """
    organization = g.get_organization("[GHEC_X]")
    return organization, organization.get_repos()

def get_updated_repos():
    """
    Get the list of updated repositories from updated_repos.csv file
    """
    updated_repos = set()
    try:
        with open('updated_repos.csv', mode='r') as file:
            csvFile = csv.reader(file)
            # Add all URLs of updated repositories to the set
            updated_repos.update(line[0] for line in csvFile)
    except FileNotFoundError:
        pass
    return updated_repos

def search_directory(path, repository, writer, repository_name, repository_org, repository_url):
    """
    Search the given directory for ".tf" files and update the contents
    """
    contents = repository.get_contents(path)
    changes_made = False
    for content in contents:
        if content.type == "file":
            if content.path.endswith(".tf"):
                file_data = repository.get_contents(content.path).decoded_content.decode()
                if "github.com/[GHEC_Y]" in file_data:
                    # update the content 
                    new_file_data = file_data.replace("github.com/[GHEC_Y]", "github.com/[GHEC_Y_updated]")
                    # Write the changes to the csv file
                    writer.writerow({'repo_name': repository_name, 'org': repository_org, 'url': repository_url, 'file_path': content.path, 'old_url': "github.com/[GHEC_Y]", 'new_url': "github.com/[GHEC_Y_updated]"})
                    changes_made = True
        elif content.type == "dir":
            changes_made = search_directory(content.path, repository, writer, repository_name, repository_org, repository_url) or changes_made
    return changes_made


def update_repo(repository, updated_repos, writer, error_count):
    """
    Check if the repository has already been updated and update the repository if needed.
    """
    try:
        repository_name = repository.name
        repository_org = repository.owner.login
        repository_url = repository.html_url
        if repository.html_url in updated_repos:
            print(f'{repository.html_url} already updated, skipping...')
            return error_count

        changes_made = search_directory("", repository, writer, repository_name, repository_org, repository_url)
        if changes_made:
            repository.create_git_commit("Update URL of terraform files", "master", [{"path": "*", "mode": "100644", "type": "blob"}])
            # Add the repository to the list of updated repositories
            updated_repos.add(repository.html_url)
            if error_count >= 100:
                print("Github API error limit reached, exiting the script")
                return error_count
        return error_count

    except Exception as e:
        error_count += 1
        with open('errors.log', mode='a') as errors_log:
            errors_log.write(f"{repository_name} : {e} \n")
        return error_count
    
def update_repositories(repositories, updated_repos):
    """
    Create the csv file and call iteration over repositories function
    """
    error_count = 0
    if os.path.isfile('updates.csv'):
        update_file = open('updates.csv', mode='a')
        iterate_over_repositories(repositories, updated_repos, writer, error_count)
    else:
        update_file = open('updates.csv', mode='w')
        fieldnames = ['repo_name', 'org', 'url', 'file_path', 'old_url', 'new_url']
        writer = csv.DictWriter(update_file, fieldnames=fieldnames)
        writer.writeheader()
        iterate_over_repositories(repositories, updated_repos, writer, error_count)
        
    print("All Done!")
    print(f"{len(updated_repos)} repositories have been updated and {error_count} had errors.")

def iterate_over_repositories(repositories, updated_repos, writer, error_count):
    """
    Iterate through all the repositories and update them if needed
    """
    for repository in repositories:
        error_count = update_repo(repository, updated_repos, writer, error_count)
        if error_count >= 100:
            break

        # Check if the rate limit has been reached (in order to verify)
        rate_limit = g.get_rate_limit()
        if rate_limit.remaining <= rate_limit.threshold:
            print("Rate limit threshold reached, waiting for reset.")
            reset_time = rate_limit.reset - datetime.utcnow()
            time.sleep(reset_time.seconds + reset_time.microseconds / 1e6)


if __name__ == "__main__":
    g = authenticate()
    organization, repositories = get_organization_and_repos(g)
    updated_repos = get_updated_repos()
    update_repositories(repositories, updated_repos)
    rate_limit = g.get_rate_limit()
    
    if rate_limit.remaining <= rate_limit.threshold:
        print("Rate limit threshold reached, waiting for reset.")
        reset_time = rate_limit.reset - datetime.utcnow()
        time.sleep(reset_time.seconds + reset_time.microseconds / 1e6)
