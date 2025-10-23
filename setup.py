from setuptools import setup, find_packages

setup(
    name="rss_content_filter",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml',
        'openai',
        'feedgen',
        'PyQt5',
        'aiohttp',
        'bilibili-api-python',
        'python-dotenv',
        'pytz'
    ],
    package_dir={'': 'src'}
) 