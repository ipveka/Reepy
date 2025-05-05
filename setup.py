from setuptools import setup, find_packages

setup(
    name="reepi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pandas>=1.4.0",
        "streamlit>=1.10.0",
        "plotly>=5.10.0",
        "python-dotenv>=0.20.0",
    ],
    author="Ignasi Pascual",
    author_email="example@example.com",
    description="A package to connect to Red Eléctrica Española API and visualize electricity data",
    keywords="electricity, API, visualization, Spain, REE",
    url="https://github.com/ipveka/REEpy",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
