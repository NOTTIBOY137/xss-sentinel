from setuptools import setup, find_packages

setup(
    name="xss-sentinel",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.28.1",
        "beautifulsoup4>=4.11.1",
        "scikit-learn>=1.1.2",
        "numpy>=1.23.2",
        "tqdm>=4.64.0",
        "colorama>=0.4.5",
      #  "tensorflow>=2.9.1",
        "joblib>=1.1.0",
    ],
    entry_points={
        'console_scripts': [
            'xss-sentinel=xss_sentinel.cli:main',
        ],
    },
)
