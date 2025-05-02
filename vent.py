import os
import sys
import wget
import csv

file_dir = os.path.dirname(os.path.abspath(__file__))

def install_package(package_name):
    print(f"Installing package: {package_name}...")

    # Define where to store installed packages (same directory as this script/executable)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    packages_dir = os.path.join(base_dir, "packages")

    # Create the directory if it doesn't exist
    os.makedirs(packages_dir, exist_ok=True)

    # Temporary directory to download the CSV
    os.makedirs(os.path.join(file_dir, "tmp"), exist_ok=True)

    # Download the packages CSV file
    csv_url = "https://sussyos.github.io/api/susScript/vent/packages.csv"
    file = wget.download(csv_url, out=os.path.join(file_dir, "tmp", "packages.csv"))

    # Read the CSV to get package information
    packages = {}
    with open(os.path.join(file_dir, "tmp", "packages.csv"), "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            packages[row['name']] = row  # Store the row by the package name

    # Check if the package exists in the CSV
    if package_name not in packages:
        print(f"Error: Unknown package '{package_name}'")
        sys.exit(1)

    # Download the package file from the URL
    package_data = packages[package_name]
    package_url = package_data["URL"]
    package_file = wget.download(package_url, out=os.path.join(packages_dir, f"{package_name}.suspkg"))

    # Extract the contents from the .suspkg file if needed
    # Assuming .suspkg is a simple script for now, not a zipped file

    # For example, you could move it directly:
    print(f"Package '{package_name}' installed successfully at {package_file}")
    # Clean up the tmp directory
    os.system(f"rmdir /s /q {os.path.join(file_dir, "tmp")}")

if __name__ == "__main__":
    match sys.argv[1]:
        case "install":
            if len(sys.argv) < 3:
                print("Usage: vent install <package_name>")
                sys.exit(1)
            install_package(sys.argv[2])
        case "update":
            # Placeholder for update functionality
            print("Update functionality is not implemented yet.")
        case _:
            print("Usage: vent.py install <package_name>")
            sys.exit(1)
