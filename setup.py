import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Giournal",
    version="0.1.0",
    author="Stefano Chiodino",
    author_email="nope@nope.nope",
    description="Encrypted journaling, git backed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StefanoChiodino/giournal",
    project_urls={
        "Bug Tracker": "https://github.com/StefanoChiodino/giournal/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'giournal=giournal.main:main',
        ],
    },
    install_requires=[
        "cffi==1.14.5",
        "cryptography==3.4.7",
        "gitdb==4.0.7",
        "GitPython==3.1.17",
        "importlib-metadata==4.0.1",
        "keyring==23.0.1",
        "pycparser==2.20",
        "python-frontmatter==1.0.0",
        "PyYAML==5.1",
        "smmap==4.0.0",
        "zipp==3.4.1",
    ],
)
