from setuptools import setup, find_packages

setup(
    name='rlway',
    version='0.0.1',
    url='https://github.com/y-plus/RLway.git',
    author='Renan HILBERT',
    author_email='renan.hilbert.ext@eurodecision.com',
    description='Railway traffic regulation using AI/RL',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    setup_requires=["wheel"],
    install_requires=[
        'networkx >= 3.0',
        'matplotlib>= 3.6.3',
        'gymnasium',
        'pandas',
        # 'pyg-lib==0.1.0+pt113cu117',
        # 'torch-scatter==2.1.0+pt113cu117',
        # 'torch-sparse==0.6.16+pt113cu117',
        # 'torch==1.13.1',
        # 'torch-geometric==2.2.0',
    ],
)
