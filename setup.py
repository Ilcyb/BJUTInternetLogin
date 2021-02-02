from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

# required = []
# with open('requirements.txt', 'r', encoding='utf-8') as f:
#     requirements = f.read().splitlines()

setup(
    name="bjut_internet_login_tool",
    version="0.1.5",
    author="ilcyb",
    author_email="hybmail1996@gmail.com",
    description="BJUT Internet Login Tool for command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ilcyb/BJUTInternetLogin",
    install_requires = [
        'requests',
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts':[
            'bjutlogin = src.main:main'
        ]
    },
)