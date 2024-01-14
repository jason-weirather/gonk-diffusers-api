from setuptools import setup, find_packages

def load_requirements(filename='requirements.txt'):
    with open(filename, 'r') as file:
        return file.read().splitlines()

setup(
    name='gonk-diffusers-api',
    version='1.1.0',
    author='Jason L Weirather',
    author_email='jason.weirather@gmail.com',
    description='A Python API for generating images with Stable Diffusion model',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jason-weirather/gonk-diffusers-api',
    packages=find_packages(),
    install_requires=load_requirements(),

    # Include additional files into the package
    package_data={
        'gonk_diffusers_api': ['static/*'],
    },

    entry_points={
        'console_scripts': [
            'gonk-diffusers-api=gonk_diffusers_api.cli:main',
        ],
    },

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
