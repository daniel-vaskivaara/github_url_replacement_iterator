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
        with open('updated_repos.csv', mode='w') as file:
            fieldname = ['updated_urls']
            writer = csv.DictWriter(file, fieldnames=fieldname)
            writer.writeheader()

    return updated_repos

def search_directory(path, repository, writer, repository_name, repository_org, repository_url):
    """
    Search the given directory for ".tf" files and update the contents
    """
    contents = repository.get_contents(path)
    changes_made = []
    for content in contents:
        if content.type == "file":
            if content.path.endswith(".tf"):
                file_data = repository.get_contents(content.path)
                if "github.com/[GHEC_Y]" in file_data.decoded_content.decode():
                    # Write the changes to the csv file
                    writer.writerow({
                        'repo_name': repository_name,
                        'org': repository_org, 
                        'url': repository_url,
                        'file_path': content.path,
                        'old_url': "github.com/[GHEC_Y]", 
                        'new_url': "github.com/[GHEC_X]"})
                    changes_made.append(content.path)
        elif content.type == "dir":
            changes_made += search_directory(content.path, repository, writer, repository_name, repository_org, repository_url)
    return changes_made




def update_repo(repository, updated_repos, error_count, writer):
    """
    Check if the repository has already been updated and update the repository if needed.
    """
    try:
        repository_name = repository.name
        repository_org = repository.owner.login
        repository_url = repository.html_url
        if repository_url in updated_repos:
            print(f'{repository_url} already updated, skipping...')
            return error_count

        changes_made = search_directory("", repository, writer, repository_name, repository_org, repository_url)
        if changes_made:
            commit_message = "Update URL of terraform files"
            master_ref = repository.get_git_ref("heads/master")
            master_sha = master_ref.object.sha
            for file_path in changes_made:
                file_data = repository.get_contents(file_path)
                new_file_data = file_data.decoded_content.decode().replace("github.com/[GHEC_Y]", "github.com/[GHEC_X]")
                repository.update_file(file_path, commit_message, new_file_data, file_data.sha, branch="master")
                repository.create_commit(commit_message, master_ref.object.sha, master_sha)
            # Add the repository to the list of updated repositories
            with open('updated_repos.csv', mode='a') as file:
                fieldname = ['updated_urls']
                writer = csv.DictWriter(file, fieldnames=fieldname)
                writer.writerow({'updated_urls':repository_url})
            if error_count >= 100:
                print("Github API error limit reached, exiting the script")
                return error_count
        return error_count

    except Exception as e:
        print(f"Error Occured: {e}")
        error_count += 1
        if error_count >= 100:
            print("Github API error limit reached, exiting the script")
            return error_count
        # Wait for some time before making next API call
        time.sleep(5)
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
