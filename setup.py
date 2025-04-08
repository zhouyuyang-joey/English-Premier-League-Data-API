from setuptools import setup, find_packages

setup(
    name="eplda",
    version="0.1.0",
    description="An unofficial API handler to footballapi.pulselive.com. Permitted for study purposes only.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Zhou Yuyang",
    author_email="joeyjoeyjoemail@163.com",
    url="https://github.com/zhouyuyang-joey/English-Premier-League-Data-API",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)