from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith('#')
    ]

runtime_requirements = [req for req in requirements if not req.startswith('pytest')]

setup(
    name='vix-index-prediction-model',
    version='1.1.0',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=runtime_requirements,
    entry_points={
        'console_scripts': [
            'run_vix_model=vix_model.app:run_training_and_generate_results'
        ]
    },
    author='OceanicPatterns',
    description='A model for predicting VIX Index prices based on volatility index',
    url='https://github.com/oceanicpatterns/VIX-Index-Prediction-Model',
)
