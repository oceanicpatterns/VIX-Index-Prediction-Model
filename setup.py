from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='vix-index-prediction-model',
    version='1.0',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'run_vix_model=ml_vix_model:run_training_and_generate_results'
        ]
    },
    author='OceanicPatterns',
    description='A model for predicting VIX Index prices based on volatility index',
    url='https://github.com/oceanicpatterns/vix-index-prediction-model',
)

