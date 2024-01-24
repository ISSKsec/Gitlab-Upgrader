import subprocess
import os
import requests
import time

def print_banner():
        banner="""
  ______   __    __      __            __              __    __                                               __
 /      \ |  \  |  \    |  \          |  \            |  \  |  \                                             |  |
|  $$$$$$\ \$$ _| $$_   | $$  ______  | $$____        | $$  | $$  ______    ______    ______   ______    ____| $$  ______    ______
| $$ __\$$|  \|   $$ \  | $$ |      \ | $$    \       | $$  | $$ /      \  /      \  /      \ |      \  /      $$ /      \  /      |
| $$|    \| $$ \$$$$$$  | $$  \$$$$$$\| $$$$$$$\      | $$  | $$|  $$$$$$\|  $$$$$$\|  $$$$$$\ \$$$$$$\|  $$$$$$$|  $$$$$$\|  $$$$$$
| $$ \$$$$| $$  | $$ __ | $$ /      $$| $$  | $$      | $$  | $$| $$  | $$| $$  | $$| $$   \$$/      $$| $$  | $$| $$    $$| $$   \$$
| $$__| $$| $$  | $$|  \| $$|  $$$$$$$| $$__/ $$      | $$__/ $$| $$__/ $$| $$__| $$| $$     |  $$$$$$$| $$__| $$| $$$$$$$$| $$
 \$$    $$| $$   \$$  $$| $$ \$$    $$| $$    $$       \$$    $$| $$    $$ \$$    $$| $$      \$$    $$ \$$    $$ \$$     \| $$
  \$$$$$$  \$$    \$$$$  \$$  \$$$$$$$ \$$$$$$$         \$$$$$$ | $$$$$$$  _\$$$$$$$ \$$       \$$$$$$$  \$$$$$$$  \$$$$$$$ \$$
                                                                | $$      |  \__| $$
                                                                | $$       \$$    $$
                                                                 \$$        \$$$$$$ @clopez"""
        print(banner)

def get_gitlab_version():
    try:
        current_version = subprocess.check_output("dpkg -l | grep gitlab-ce | awk '{print $3}'", shell=True, text=True).strip()
        return current_version
    except subprocess.CalledProcessError:
        print("Error obtaining the current GitLab version.")
        return None

def install_gitlab_package(package_path):
    try:
        os.system(f"sudo dpkg -i {package_path}")
        os.system("sudo apt-get install -f")  # Install missing dependencies if any
        return True
    except Exception as e:
        print(f"Error during package installation: {e}")
        return False

def download_package(download_url, package_path):
    try:
        response = requests.get(download_url, allow_redirects=True)
        if response.status_code == 200:
            with open(package_path, 'wb') as f:
                f.write(response.content)
            return True
        elif response.status_code == 404:
            print("The requested version does not exist.")
            return False
        else:
            print(f"Error downloading the package. Response code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error downloading the package: {e}")
        return False

def main():
    print_banner()
    time.sleep(2)
    current_version = get_gitlab_version()
    if current_version is None:
        return

    print(f"Current GitLab version: {current_version}")

    version_parts = current_version.split('.')
    version_numbers = [int(part) if part.isdigit() else part for part in version_parts]

    # Variable to count iterations
    iteration_count = 0

    while iteration_count < 12:
        # Increment the middle part of the version
        version_numbers[1] += 1

        # If the middle part reaches 13, also increment the left part
        if version_numbers[1] == 13:
            version_numbers[0] += 1
            version_numbers[1] = 0

        next_version = ".".join(map(str, version_numbers))

        print(f"Iteration {iteration_count + 1}: Downloading and installing version: {next_version}")

        download_url = f"https://packages.gitlab.com/gitlab/gitlab-ce/packages/debian/buster/gitlab-ce_{next_version}_amd64.deb/download.deb"

        print(f"Downloading from: {download_url}")

        package_path = f"/tmp/gitlab-ce_{next_version}.deb"
        download_success = download_package(download_url, package_path)

        if not download_success:
            # Download has failed, but now check if it was a 404 error
            iteration_count += 1  # Increment the counter
            continue

        install_success = install_gitlab_package(package_path)

        if not install_success:
            print("Package installation has failed. Continuing with the next version.")
            iteration_count += 1  # Increment the counter
            continue

        # Check if a new version is installed
        new_version = get_gitlab_version()

        # If the new version is the same as the current one, skip to the next loop cycle
        if new_version == current_version:
            print(f"Version {next_version} already installed. Continuing with the next version.")
            iteration_count += 1  # Increment the counter
            continue

        if new_version == current_version:
            print("No new versions available.")
            break

        current_version = new_version
        iteration_count += 1  # Increment the counter

    print("Finished\nIf you believe there are more versions, run the script again")

if __name__ == "__main__":
    main()
