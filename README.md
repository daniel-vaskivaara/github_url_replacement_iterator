# URL Update Script

This script is used to update the URLs of a specific file type in all the repositories of a Github Enterprise Cloud organization. 
It will also commit the changes made to the repository and keeps a record of the updated repositories in a csv file.

## Features

- Authentication to Github Enterprise Cloud X
- Retrieval of all repositories in the organization
- Searching for a specific file type in the repositories
- Updating the URLs in the file and committing the changes to the repository
- Keeping track of the repositories that have been updated in a csv file

## How to use
1. Replace the `access_token` variable in the `authenticate()` function with your own Github Enterprise Cloud X access token.
2. Replace `"[GHEC_X]"` with the name of your Github Enterprise Cloud organization in the `get_organization_and_repos()` function.
3. Replace `"[GHEC_Y]"` with the old URL that you want to replace in the `search_directory()` and `update_repo()` functions.
4. Replace `"[GHEC_X]"` with the new URL that you want to use in the `search_directory()` and `update_repo()` functions.
5. Run the script and wait for it to complete.
6. Check the updated_repos.csv file for the list of updated repositories.

## Notes
- This script assumes that the updated_repos.csv file already exists, if this is not the case it will create the file with the required fields.
- Be cautious when running the script with actual values and on the actual repository, this script will make changes on the repository it is run on.
- Error handling has not been added on some parts of the script, it would be good to add it before running in production.

## Technical Details

- This script is designed to search through all repositories within a specified Github organization and look for files with the ".tf" file extension. Within these files, it looks for instances of a specific URL (in this case, `"github.com/[GHEC_Y]"`) and replaces them with a new URL (in this case, `"github.com/[GHEC_X]"`). 
- The script uses the Github Python API to interact with the organization's repositories and make the necessary updates.
- Additionally, the script tracks which repositories have been updated by maintaining a list in a CSV file. The script checks this list before updating a repository to avoid unnecessary updates.
- It also includes a mechanism for handling rate limiting from the Github API by returning an error count when the API rate limit is reached.
- The reason behind this mechanism, is that the `Github API` uses `OAuth` `(OAuth2)` for authentication, which allows users to make a certain number of requests per hour. 
- The exact number of requests that user are allowed to make depends on the plan that organisation is using. For example, the free plan allows for 60 requests per hour, while the more advanced plans allow for a higher number of requests. This can be a limitation if script makes lots of requests, as it may hit the rate limit and stop working. 
- The script will throw an exception in that case, user shoud handle the exception to check whether the limit has been reached or not. 
- User could use exponential backoff to handle the rate limits or use the retry library. This will retry the request when it gets a rate limiting error. The script will slow down when it is near the rate limit but will not stop.
- If the repository has not been updated previously and changes have been made, it creates a commit with the message "Update URL of terraform files" on the master branch and adds the repository to the list of updated repositories in the `updated_repos.csv` file. If there is an error, the error count is returned and checked for an API limit being reached.
- Overall, this script can help automate a process of updating the terraform files, which could be a cumbersome and time-consuming task if done manually.


## Limitations
- `Access token` is used for authenticate to the `Github API`, If the token is not correct or expired, the script will not be able to authenticate and access the organization's repositories.
- Rate limit for the `Github API` can be achieved during the exection, because the number of requests that can be made within a certain time frame. If the script reaches this limit, it will not be able to access the API until the rate limit resets.
- The script only searches and updates files with the `".tf"` extension in the `root` directory of the repository and its `sub-directories`. It will not update files with other extensions or in other locations.
- The script writes the changes to the repositories to the `master branch` of the repository.
- Script does not check for pre-existing files `updated_repos.csv`, if file does not exist it will create new one and continue working.
- The script needs to be tested properly.
- The script has not been tested on repositories with a large number of files. The execution time of the script will depend on several factors, including the number of repositories in the organization, the number of `".tf"` files in each repository, the size of each `".tf"` file, and the internet connection speed. If the organization has a large number of repositories or each repository has a large number of `".tf"` files, the script may take a significant amount of time to complete. Additionally, if the script encounters rate limiting from the GitHub API, it will pause execution for a period of time specified in the API's response headers, which could add to the execution time. However, the script uses caching to avoid repetitive execution on the same repositories and so the execution will be faster over time.
- It's difficult to give an estimate of how long the script would take to run, as it would depend on users specific use case and circumstances.