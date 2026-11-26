import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'fossbot_click_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jakub Piwosz',
    maintainer_email='kubas.p1003@gmail.com',
    description='TODO: Package description',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'click_controller = fossbot_click_control.click_controller:main',
            'dashboard = fossbot_click_control.dashboard:main',
        ],
    },
)
