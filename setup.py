from setuptools import setup, find_packages

setup(
    name="SyncHero",  # Package name
    version="0.1",  # Initial version
    description="A CLI tool for quick and easy file backups",  # Short description
    long_description="A CLI tool for quick and easy file backups, made to learn CLI tool development. It simply automates copying files between two directories.",  # Detailed description
    long_description_content_type="text/markdown",  # Content type for detailed description
    author="Yunus-38",  # Your name
    author_email="107210213+Yunus-38@users.noreply.github.com",  # Your email
    url="https://github.com/Yunus-38/SyncHero",  # GitHub or project link
    packages=find_packages(),  # Automatically find your package
    py_modules=["SyncHero"],  # Include single-module scripts like SyncHero.py
    entry_points={
        "console_scripts": [
            "synchero=synchero.__main__:main",  # CLI command -> script:entry_function
        ]
    },
    include_package_data=True,
    install_requires=[],  # List dependencies if you have any (e.g., ["requests"])
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
)
