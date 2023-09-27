import os
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np
from math import floor, ceil
from datetime import datetime
import pandas as pd
import argparse


def sorter(files):
    """
        Sorts the files into either in-distribution or out-of distribution list
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


def get_save_path(subject_number, dist_type, experiment_type, view, name, frame_num):
    """
    Returns the path where the label will be saved
    """
    save_path = f"./images/Test_Subject_{subject_number}/{dist_type}/{experiment_type}/{view}/{name}_{frame_num}.png"
    return save_path


def choose_frames(files, view, dist_type, subject_number, frames_to_sample, initial_frame):
    """
    Collects an equally distributed sample of frames from the videos sent in 
    and saves the unlabelled frames to its respective folder location.
    """

    for i, file in enumerate(files):
        name = file
        file = VideoFileClip(
            f"./videos/Test_Subject_{subject_number}/{view}" + f"/{file}")

        num_frames = int(file.fps * file.duration)

        # Find frames to sample for this file. We have to int cast it for np.linspace
        # Note: We don't expect `frames_to_sample` to be less than the number of files
        num_samples = int(frames_to_sample / len(files))

        print(f"the sampling interval is {num_samples}")

        # Here we get an equal distribution of frames from the initial frame defined and the last frame of the video
        if num_samples > 2:
            frame_numbers = np.linspace(
                initial_frame, num_frames, num_samples).tolist()
        if num_samples == 2:
            frame_numbers = np.linspace(initial_frame, num_frames, 4).tolist()
            frame_numbers = frame_numbers[1:3]
        frame_numbers = [int(floor(frame_num)) for frame_num in frame_numbers]

        # Moviepy only takes time in seconds to return a frame, so we calculate the time(s) of the video
        # using the frame we want and the FPS of the video
        frame_numbers = np.array(frame_numbers, dtype=float)
        frame_times = frame_numbers * (1 / file.fps)
        # We have to floor each time otherwise the last frame runs us into problems
        frame_times = np.floor(frame_times)

        frames = []
        for time in frame_times:
            try:
                frames.append(file.get_frame((time)))
            except:
                time -= 1
                frames.append(file.get_frame((time)))

        # Going through each frame and saving it as an image
        final_frame_nums = []
        for frame, frame_num in zip(frames, frame_numbers):
            name = name.split(".")[0]
            experiment_type = name.split("_")[0]

            save_path = get_save_path(
                subject_number, dist_type, experiment_type, view, name, frame_num)

            # Checking if a file with the same frame number already exists
            # If it does, check if the next frame in the video also already exists
            if os.path.isfile(save_path):
                while True:
                    frame_num += 1
                    save_path = get_save_path(
                        subject_number, dist_type, experiment_type, view, name, frame_num)

                    if os.path.isfile(save_path):
                        continue
                    else:
                        frame_time = floor(frame_num * (1 / file.fps))
                        frame = file.get_frame(float(frame_time))
                        break
            final_frame_nums.append(frame_num)
            image = Image.fromarray(frame)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            image.save(save_path)

        # Saving this as a CSV file instead
        csv_file_path = f"./images/Test_Subject_{subject_number}/{dist_type}/{experiment_type}/{view}/labelhistory.csv"
        data = []
        data.append({
            "file name": name,
            "Time of file writes": datetime.now(),
            "Initial frame": initial_frame,
            "Frame nums saved": final_frame_nums
        })
        df = pd.DataFrame(data)

        csv_file_exists = os.path.exists(csv_file_path)

        df.to_csv(csv_file_path, mode='a', index=False,
                  header=not csv_file_exists)


def extract_frames(participant, frames, view, dist_type, output_dir, initial_frame, csv_path):
    top_files = os.listdir(f"./videos/Test_Subject_{participant}/{view}")
    id_files, ood_files = sorter(top_files)  # use ood?

    id_count = frames // 2
    ood_count = frames - id_count

    print(
        f"Sampling {id_count} in-distribution and {ood_count} out-of-distribution frames from {view} view.")

    for i, file in enumerate(id_files[:id_count]):
        name = file
        file = VideoFileClip(
            f"./videos/Test_Subject_{participant}/{view}/{file}")

        num_frames = int(file.fps * file.duration)
        frame_numbers = np.linspace(
            initial_frame, num_frames, frames, endpoint=False).astype(int)

        frames = []
        for frame_num in frame_numbers:
            frame_time = frame_num * (1 / file.fps)
            frames.append(file.get_frame(frame_time))

        for frame_num, frame in zip(frame_numbers, frames):
            experiment_type = name.split("_")[0]
            save_path = get_save_path(
                participant, dist_type, experiment_type, view, name, frame_num)

            while os.path.isfile(save_path):
                frame_num += 1
                frame_time = frame_num * (1 / file.fps)
                frame = file.get_frame(frame_time)
                # save_path = get_save_path(
                #     participant, dist_type, experiment_type, view, name, frame_num)
                save_path = os.path.join(output_dir, get_save_path(
                    participant, dist_type, experiment_type, view, name, frame_num))

            image = Image.fromarray(frame)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            image.save(save_path)

    # Saving frames as CSV
    frame_info = []

    for frame_num in frame_numbers:
        # This line assumes experiment_type is the same for all frames
        experiment_type = name.split("_")[0]
        frame_info.append({
            "Frame Number": frame_num,
            "Participant": participant,
            "Distribution Type": dist_type,
            "View": view,
            "Experiment Type": experiment_type
        })

    frame_info_df = pd.DataFrame(frame_info)

    # Check if the CSV file already exists
    csv_file_exists = os.path.exists(csv_path)

    # Append to the CSV file if it exists, otherwise create a new one
    frame_info_df.to_csv(csv_path, mode='a', index=False,
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
    parser.add_argument('-d', '--dist-type', required=True,
                        choices=["id", "ood"], help="Distribution type")
    parser.add_argument('-o', '--output-dir', required=True,
                        help="Output directory for sampled frames")
    parser.add_argument('-i', '--initial-frame', type=int,
                        default=0, help="Initial frame for sampling")
    parser.add_argument('-c', '--csv-path', required=True,
                        help="Path for CSV file")

    args = parser.parse_args()

    # Call the extract_frames function with command-line arguments
    extract_frames(args.participant, args.frames, args.view,
                   args.dist_type, args.output_dir, args.initial_frame, args.csv_path)
