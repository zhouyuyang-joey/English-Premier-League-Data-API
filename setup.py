from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eplda",
    version="0.2.3",
    description="An unofficial lightweight Python client library for Premier League Data API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zhou Yuyang",
    author_email="joeyjoeyjoemail@163.com",
    url="https://github.com/zhouyuyang-joey/English-Premier-League-Data-API",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'eplda': ['config.yaml'],
    },
    install_requires=requirements,
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'black', 'flake8'],
        'test': ['pytest', 'pytest-mock']
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="premier-league football soccer api data statistics",
    project_urls={
        "Bug Reports": "https://github.com/zhouyuyang-joey/English-Premier-League-Data-API/issues",
        "Source": "https://github.com/zhouyuyang-joey/English-Premier-League-Data-API",
        "Documentation": "https://github.com/zhouyuyang-joey/English-Premier-League-Data-API/blob/main/README.md",
    },
)