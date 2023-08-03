# Template Python
This is a template repository that serves as a starting point for all _CTS-IT_ python packages. To learn more about template repos, read the [official documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

## Getting Started
To create a repository from this template:
1. On GitHub.com, navigate to the main page of the repository.
2. Above the file list, click Use this template.
3. Select Create a new repository.
> ![use template to create repository](https://docs.github.com/assets/cb-77734/mw-1440/images/help/repository/use-this-template-button.webp)

## Creating Python Package
1. Clone the repo
1. Open the project in VSCode
1. In VSCode find all occurences of `package_name` and `PackageName` using `cmd + shift + f` and replace with your desired package name e.g. `ctsit_python_utils`.
2. Verify that the package works. From the project root:
    - Create the virtual environment: `python3 -m venv .venv`
    - Activate the virtual environment `source .venv/bin/activate`
    - Install the package `pip install .`
    - Run the unit tests `python -m unittest -v`. 1 out 1 tests should pass
    - Run `$ <package_name> --help`
