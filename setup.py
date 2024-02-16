from setuptools import setup, find_packages

setup(
    name='rlway',
    version='0.0.5',
    url='https://github.com/y-plus/RLway.git',
    author='Renan HILBERT',
    author_email='renan.hilbert.ext@eurodecision.com',
    description='Railway traffic regulation using AI/RL',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["*.jar"]},
    python_requires=">=3.10",
    setup_requires=["wheel"],
    install_requires=[
        'gymnasium',
        # 'pyg-lib==0.1.0+pt113cu117',
        # 'torch-scatter==2.1.0+pt113cu117',
        # 'torch-sparse==0.6.16+pt113cu117',
        # 'torch==2.0.0',
        # 'torch-geometric==2.2.0',
        'networkx >= 3.0',
        'matplotlib>= 3.6.3',
        'pandas',
        "python-dotenv",
        "folium",
        "plotly",
        "haversine",
        "typing-inspect>=0.8.0",
        "typing_extensions>=4.5.0",
        'railjson_generator @ git+ssh://git@github.com/osrd-project/osrd.git@v0.1.4#subdirectory=python/railjson_generator',  # noqa
        'ipython',
    ],
)
