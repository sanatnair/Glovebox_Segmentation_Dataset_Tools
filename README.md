# Frame Extraction Tool

This is a video frame extraction tool designed to process and extract frames from the glovebox segmentation dataset. Allows users to capture specific frames for use in analysis and training data.

### Key Features

- Extract frames from the video files in the dataset, providing a sample of frames for analysis.
- Extraction based on user-specified parameters provided in the command-line interface (CLI).
- Parameters include participant number, number of frames to sample, initial frame for sampling, specific video view (Top View / Side View), and specific distribution type (In-distribution / Out-of-distribution).
- Saves and organizes frames as PNG files for further use, with the option to specify the frame output directory path in the CLI.
- Automatically creates and updates a CSV file with information about the frames extracted, including timestamps and frame numbers, with the option to specify the CSV output directory path in the CLI.

## Installation

To use the frame extraction tool, you'll need to follow these steps:

### 1. Clone the Repository

Clone the repository to your local machine using `git`:

```
git clone https://github.com/sanatnair/Glovebox_Segmentation_Dataset_Tools
```

### 2. Create a Virtual Environment (Optional, but Recommended)

Using `virtualenv` (recommended for Python virtual environment):

```
# Install virtualenv if you haven't already
pip install virtualenv

# Create a virtual environment
virtualenv glovebox_env

# Activate the virtual environment
source glovebox_env/bin/activate
```

Using `conda` (if you prefer Conda environments):

```
# Create a Conda environment
conda env create -f environment.yml

# Activate the Conda environment
conda activate glovebox_tool
```

### 3. Install Dependencies

Install the required Python packages using `pip`:

```
pip install -r requirements.txt
```

### 4. Run the Tool

You can now run the frame extraction tool with the desired command-line arguments outlined in the [Usage](#usage) section

## Usage

1. Ensure glovebox dataset video files are saved in the [videos](/videos) folder as outlined in the videos [README](/videos/README.md)
2. Run the script using the command line interface as follows:

```
python frame_extraction.py -p PARTICIPANT_NUMBER -f NUM_FRAMES -v VIEW -d DISTRIBUTION_TYPE -o OUTPUT_DIR -i INITIAL_FRAME -c CSV_PATH
```

EXAMPLE:

```
python frame_extraction.py -p 2 -f 4 -v Side_View -d id -o test_images -i 10 -c test_csv
```

_This command will generate four equally spaced in-distribution frames from the Side View of participant 2, starting at the initial frame of 10. The extracted frames will be created and/or saved in the `test_images` folder, and the CSV files will be stored in the `test_csv` folder, both within the same directory_

**Note: Required arguments include `PARTICIPANT_NUMBER`, `NUM_FRAMES`, and `VIEW`. Input for `PARTICPANT_NUMBER` ranges from available files and `VIEW` includes 'Side_View' or 'Top_View'. If `INITIAL_FRAME` is not provided, it will defualt to initial frame = 0. If `DISTRIBUTION_TYPE` ['ood', 'id', 'all'] is not provided, it will default to the equal sampling of both. Finally, `OUTPUT_DIR` and `CSV_PATH` will find and/or create the path if provided, else automatically create a path if not provided**
