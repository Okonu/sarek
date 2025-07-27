#!/usr/bin/env python3
"""
Setup script for Sarek AI Assistant
"""

from setuptools import setup, find_packages

setup(
    name="sarek",
    version="1.0.0",
    description="Advanced Terminal AI Assistant",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "rich>=10.0.0",
        "GitPython>=3.1.0",
        "SpeechRecognition>=3.8.0",
        "pyttsx3>=2.90",
        "psutil>=5.8.0",
    ],
    entry_points={
        'console_scripts': [
            'sarek=sarek.main:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)