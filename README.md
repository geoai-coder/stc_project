# Project Documentation

## Overview
This directory contains the core files and folders of the project. Below is a detailed description of each component.

## Files and Folders

- **dataset**
  - **Description**: Contains all the datasets used in the project.
  - **Importance**: The dataset is the foundation of project analysis.

- **plotpreocess**
  - **Description**: Folder for scripts that process and plot data result histograms.
  - **Purpose**: Used for data visualization to help understand data distribution.

- **pm_exper**
  - **Description**: Contains experimental scripts for the second module of spatiotemporal correlation pattern matching.
  - **Functionality**: Implements matching and verification of spatiotemporal correlation patterns.

- **static**
  - **Description**: Stores static files such as stopwords, tuple types, etc.
  - **Application**: Provides static resources required for project operation.

- **stcTest**
  - **Description**: Contains some task test scripts.
  - **Purpose**: To ensure the stability and reliability of each module of the project.

- **stc_analysis**
  - **Description**: Contains statistical analysis, i.e., feature processing scripts for the first module of spatiotemporal correlation calculation.
  - **Importance**: Feature processing is a key step in data analysis.

- **test**
  - **Description**: Folder for test scripts and test cases.
  - **Importance**: Ensures code quality and project stability.

- **tools**
  - **Description**: Contains utility scripts and tools used in the project, such as ltp tools, global variable settings, etc.
  - **Functionality**: Improves development efficiency and code maintainability.

- **Documentation0929_en.md**
  - **Description**: The English version of the document created on 09/29, used to explain the results of all processes of the project.
  - **Purpose**: Provides detailed guidance and reference for project users.

- **main_stc_pm.py**
  - **Description**: The main script, including tasks such as spatiotemporal correlation calculation, statistical analysis, spatiotemporal correlation pattern determination, and spatiotemporal correlation pattern matching.
  - **Core Functionality**: The main execution file of the project, driving the entire analysis process.

## Usage
To use GeoAI Coder, please follow these steps:

1. **Setup**: Ensure all dependencies are installed.
   - Check the `requirements.txt` file and use the `pip install -r requirements.txt` command to install dependencies.

2. **Data**: Place your dataset in the `Dataset` folder.
   - Ensure the dataset format complies with project requirements.

3. **Run Scripts**: Execute the scripts in the corresponding folders as needed.
   - Use command line tools to run `main_stc_pm.py` or other scripts.

4. **View Documentation**: Refer to `Documentation0929_en.md` for detailed instructions.
   - The document provides detailed guidelines for project use and development.

## Contributing
Contributions are welcome. Please follow the guidelines in the `CONTRIBUTING.md` file.

## License
This project is licensed under the [MIT License](LICENSE).

---

This document provides a high-level overview of the GeoAI Coder project structure. For more detailed information, please refer to the individual documentation files.
