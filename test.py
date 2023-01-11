import csv
from github import Github
import time
from datetime import datetime


if __name__ == "__main__":
    # authenticate to Github Enterprise Cloud X
    g = Github("access_token")

    # Get the organization for which we want to update the repositories
    organization = g.get_organization("[GHEC_X]")

    # Get all repositories for the organization
    repositories = organization.get_repos()

    # Create a set to store updated repositories
    updated_repos = set()
    try:
        with open('updated_repos.csv', mode='r') as file:
            csvFile = csv.reader(file)
            # Add all URLs of updated repositories to the set
            updated_repos.update(line[0] for line in csvFile)
    except FileNotFoundError:
        pass

    error_count = 0

    # Open a csv file to log all updates
    with open('updates.csv', mode='a') as update_file:
        fieldnames = ['repo_name', 'org', 'url', 'file_path', 'old_url', 'new_url']
        writer = csv.DictWriter(update_file, fieldnames=fieldnames)
        writer.writeheader()

        # Open a file to log errors
        with open('errors.log', mode='w') as errors_log:

            # Iterate through all repositories
            for repository in repositories:
                # Check if the repository has already been updated
                if repository.html_url in updated_repos:
                    print(f'{repository.html_url} already updated, skipping...')
                    continue

                try:
                    repository_name = repository.name
                    repository_org = repository.owner.login
                    repository_url = repository.html_url

                    changes_made = False

                    def search_directory(path):
                        contents = repository.get_contents(path)
                        for content in contents:
                            if content.type == "file":
                                # Check if the file is a terraform script
                                if content.path.endswith(".tf"):
                                    file_data = repository.get_contents(content.path).decoded_content.decode()
                                    if "github.com/[GHEC_Y]" in file_data:
                                        # update the content 
                                        new_file_data = file_data.replace("github.com/[GHEC_Y]", "github.com/[GHEC_Y_updated]")
                                        # Write the changes to the csv file
                                        writer.writerow({'repo_name': repository_name, 'org': repository_org, 'url': repository_url, 'file_path': content.path, 'old_url': "github.com/[GHEC_Y]", 'new_url': "github.com/[GHEC_Y_updated]"})
                                        changes_made = True
                            elif content.type == "dir":
                                search_directory(content.path)
                        return changes_made

                    search_directory("")
                    if changes_made:
                        repository.create_git_commit("Update URL of terraform files", "master", [{"path": "*", "mode": "100644", "type": "blob"}])
                    # Add the repository to the list of updated repositories
                    updated_repos.add(repository.html_url)
                    if error_count >= 100:
                        print("Github API rate limit reached, exiting the script")
                        break
                except Exception as e:
                    error_count +=1
                    errors_log.write(f"{repository_name} : {e} \n")
                    continue
                
            # Check if the rate limit has been reached (in order to verify)
            rate_limit = g.get_rate_limit()
            if rate_limit.remaining <= rate_limit.threshold:
                print("Rate limit threshold reached, waiting for reset.")
                reset_time = rate_limit.reset - datetime.utcnow()
                time.sleep(reset_time.seconds + reset_time.microseconds / 1e6)


        print("All Done!")
        print(f"{len(updated_repos)} Repositories have been updated.")
        print(f"{error_count} Repositories had errors.")
        csvFile.close()
        errors_log.close()