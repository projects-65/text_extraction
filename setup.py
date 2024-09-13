from setuptools import setup, find_packages

setup(
    name='your-flask-app',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==2.0.1',
        'PyPDF2==1.26.0',
        'joblib==1.0.1'
    ],
)
