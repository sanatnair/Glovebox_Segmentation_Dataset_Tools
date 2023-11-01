import os
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np
from math import floor, ceil
from datetime import datetime
import pandas as pd
import argparse
from typing import List, Tuple, Optional


def sorter(files: List[str]) -> Tuple[List[str], List[str]]:
    """
    Sorts the input file names into in-distribution (ID) and out-of-distribution (OOD) lists.
    
    Args:
        files (List[str]): List of file names to be sorted.
        
    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists - ID files and OOD files.
    """

    id = []
    ood = []
    for file in files:
        parse = file.split("_")[1]
        # if the file has gloves
        if parse.startswith("GL"):
            # if it is not a green screen video, it is ID (because green screen is mentioned in the last part of the file naming convention)
            if (file.split("_")[-1]).startswith("GL"):
                id.append(file)
            # if it is a green screen video, it is OOD
            else:
                ood.append(file)
        # if there are no gloves in the video, it is OOD
        elif parse.startswith("NG"):
            ood.append(file)
        else:
            print(f"lonely {file}")
    return id, ood

def extract_frames(participant: int, frames: int, view: str, dist_type: str, 
                   output_dir: str, initial_frame: int, csv_path: Optional[str] = None) -> None:
    """
    Collects an equally distributed sample of frames from the specified videos
    and saves the unlabelled frames to their respective folder locations.
    
    Args:
        participant (int): Participant number.
        frames (int): Number of frames to sample.
        view (str): Video view ('Top_View' or 'Side_View').
        dist_type (str): Distribution type ('id' for in-distribution, 'ood' for out-of-distribution).
        output_dir (str): Output directory for sampled frames.
        initial_frame (int): Initial frame for sampling.
        csv_path (str, optional): Path for the CSV file.

    Returns:
        None
    """

    def get_save_path(subject_number: int, dist_type: str, experiment_type: str, view: str, 
                  name: str, frame_num: int, output_dir: Optional[str] = None) -> str:
        """
        Returns the path where the label will be saved.
        
        Args:
            subject_number (int): Participant number.
            dist_type (str): Distribution type ('id' or 'ood').
            experiment_type (str): Experiment type.
            view (str): Video view ('Top_View' or 'Side_View').
            name (str): File name.
            frame_num (int): Frame number.
            output_dir (str, optional): Output directory for sampled frames.

        Returns:
            str: The path where the label will be saved.
        """

        if output_dir:
            save_path = os.path.join(f"{output_dir}/Test_Subject_{subject_number}/{dist_type}/{experiment_type}/{view}/{name}_{frame_num}.png")
        else:
            save_path = f"./images/Test_Subject_{subject_number}/{dist_type}/{experiment_type}/{view}/{name}_{frame_num}.png"
        return save_path
    
    # identify and sort specified files
    try:
        top_files = os.listdir(f"./videos/Test_Subject_{participant}/{view}")
    except FileNotFoundError:
        print('It seems the participant requested is not in the dataset files. '
              'Please revise the CLI argument and/or the video file directory.')
        return
    id_files, ood_files = sorter(top_files)

    # visual output of specified parameters 
    try:
        if dist_type == "ood":
            selected_files = ood_files
            dist_type_print = 'out-of-distribution'
            print(f"Sampling {frames} {dist_type_print} frames from {view} view.")
            frames_per_file = frames // len(selected_files)
        elif dist_type == "id":
            selected_files = id_files
            dist_type_print = 'in-distribution'
            print(f"Sampling {frames} {dist_type_print} frames from {view} view.")
            frames_per_file = frames // len(selected_files)
    except ZeroDivisionError:
        print('It seems that the requested distribution type is not found for the specified participant and view. '
              'Please revise the CLI argument and/or the video file directory.')
        return

    print(f"Frames sampled per file is {frames_per_file}.")

    # extract frames from each video file
    for i, file in enumerate(selected_files):
        
        name = file

        file = VideoFileClip(
            f"./videos/Test_Subject_{participant}/{view}" + f"/{file}")

        num_frames = int(file.fps * file.duration)

        # recall frames to sample for this file
        num_samples = frames_per_file

        # here we get an equal distribution of frames from the initial frame defined and the last frame of the video
        try:
            if num_samples == 1:
                frame_numbers = np.linspace(initial_frame, num_frames, 5).tolist()
                frame_numbers = [frame_numbers[2]]  # Select the third frame
            if num_samples > 2:
                frame_numbers = np.linspace(
                    initial_frame, num_frames, num_samples).tolist()
            if num_samples == 2:
                frame_numbers = np.linspace(initial_frame, num_frames, 4).tolist()
                frame_numbers = frame_numbers[1:3]
            frame_numbers = [int(floor(frame_num)) for frame_num in frame_numbers]
        except OSError:
            print('It seems the requested initial frame and/or number of frames exceeds the available amount of frames. '
                  'Please revise the CLI argument and/or check the status of the video file(s)')
            return

        # moviepy only takes time in seconds to return a frame, so we calculate the time(s) of the video
        # using the frame we want and the FPS of the video
        frame_numbers = np.array(frame_numbers, dtype=float)
        frame_times = frame_numbers * (1/file.fps)
        
        # we have to floor each time otherwise the last frame runs us into problems
        frame_times = np.floor(frame_times)

        frames = []
        for time in frame_times:
            try:
                frames.append(file.get_frame((time)))
            except:
                time -= 1
                frames.append(file.get_frame((time)))

        # going through each frame and saving it as an image
        final_frame_nums = []
        for frame, frame_num in zip(frames, frame_numbers):
            name = name.split(".")[0]
            experiment_type = name.split("_")[0]

            save_path = get_save_path(
                participant, dist_type, experiment_type, view, name, frame_num)

            # checking if a file with the same frame number already exists
            # if it does, check if the next frame in the video also already exists
            if os.path.isfile(save_path):
                while True:
                    frame_num += 1
                    save_path = get_save_path(
                        participant, dist_type, experiment_type, view, name, frame_num)

                    if os.path.isfile(save_path):
                        continue
                    else:
                        frame_time = floor(frame_num * (1/file.fps))
                        frame = file.get_frame(float(frame_time))
                        break
            final_frame_nums.append(frame_num)
            image = Image.fromarray(frame)

            # saving frames in specified output directiory
            if output_dir:
                os.makedirs(f"{output_dir}/Test_Subject_{participant}/{dist_type}/{experiment_type}/{view}/", exist_ok=True)
                image.save(get_save_path(participant, dist_type, experiment_type, view, name, frame_num, output_dir))
            else:
                os.makedirs(
                    f"./images/Test_Subject_{participant}/{dist_type}/{experiment_type}/{view}/", exist_ok=True)
                image.save(get_save_path(participant, dist_type, experiment_type, view, name, frame_num, output_dir))

        # saving info as csv file in specified directory
        if csv_path:
            csv_directory = os.path.join(csv_path, f"Test_Subject_{participant}/{dist_type}/{experiment_type}/{view}")
            os.makedirs(csv_directory, exist_ok=True)
            csv_file_path = os.path.join(csv_directory, 'labelhistory.csv')
        # if csv directory not specified but output directory is
        elif output_dir:
            csv_file_path = f"{output_dir}/Test_Subject_{participant}/{dist_type}/{experiment_type}/{view}/labelhistory.csv"
        # if neither directory is specified
        else:
            csv_file_path = f"./images/Test_Subject_{participant}/{dist_type}/{experiment_type}/{view}/labelhistory.csv"
        data = []
        data.append({
            "File name": name,
            "Time of file writes": datetime.now(),
            "Initial frame": initial_frame,
            "Frame nums saved": final_frame_nums
        })
        df = pd.DataFrame(data)

        csv_file_exists = os.path.exists(csv_file_path)

        df.to_csv(csv_file_path, mode='a', index=False,
                  header=not csv_file_exists)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Video Frame Extraction Script")

    # Define command-line arguments
    parser.add_argument('-p', '--participant', type=int,
                        required=True, help="Participant number")
    parser.add_argument('-f', '--frames', type=int,
                        required=True, help="Number of frames to sample")
    parser.add_argument('-v', '--view', required=True,
                        choices=["Top_View", "Side_View"], help="Video view")
    parser.add_argument('-d', '--dist-type', default=None, choices=["id", "ood"], help="Distribution type")
    parser.add_argument('-o', '--output-dir', default=None,
                        help="Output directory for sampled frames")
    parser.add_argument('-i', '--initial-frame', type=int,
                        default=0, help="Initial frame for sampling")
    parser.add_argument('-c', '--csv-path', default=None,
                        help="Path for CSV file")

    args = parser.parse_args()

    # Call the extract_frames function with command-line arguments
    if args.dist_type == "ood":
        extract_frames(args.participant, args.frames, args.view,
            args.dist_type, args.output_dir, args.initial_frame, args.csv_path)
    elif args.dist_type == "id":
        extract_frames(args.participant, args.frames, args.view,
            args.dist_type, args.output_dir, args.initial_frame, args.csv_path)
    # If dist_type is not explicitly specified, split between ID and OOD
    else: 
        sample_frames = args.frames // 2
        extract_frames(args.participant, sample_frames, args.view,
            'id', args.output_dir, args.initial_frame, args.csv_path)
        extract_frames(args.participant, sample_frames, args.view,
            'ood', args.output_dir, args.initial_frame, args.csv_path)