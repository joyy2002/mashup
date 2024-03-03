import os
import sys
from googleapiclient.discovery import build
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pytube import YouTube

class InvalidInputError(Exception):
    pass

def get_youtube_video_links(singer_name, num_results=5):
    api_key = "AIzaSyDZOv0RJqlFNVj13WKh4vRyEkiBLr7wMJg"
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Search for videos related to the singer's name
    search_response = youtube.search().list(
        q=singer_name,
        part='id',
        maxResults=num_results,
        type='video'
    ).execute()

    video_links = []
    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_links.append(f"https://www.youtube.com/watch?v={video_id}")

    return video_links

def download_youtube_videos(video_links, output_dir):
    for i, video_link in enumerate(video_links, start=1):
        try:
            yt = YouTube(video_link)
            stream = yt.streams.get_highest_resolution()
            print(f"Downloading video {i}/{len(video_links)}: {yt.title}")
            stream.download(output_dir)
        except Exception as e:
            raise RuntimeError(f"Error downloading video {i}/{len(video_links)}: {e}")

def convert_videos_to_audio(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"):
            video_path = os.path.join(directory, filename)
            base, _ = os.path.splitext(filename)
            output_path = os.path.join(directory, f"{base}.mp3")
            try:
                video = VideoFileClip(video_path)
                video.audio.write_audiofile(output_path)
                print(f"Converted {filename} to audio!")
            except Exception as e:
                raise RuntimeError(f"Error converting {filename}: {e}")

def cut_audio_files(n_seconds, directory):
    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            audio_path = os.path.join(directory, filename)
            base, ext = os.path.splitext(filename)
            try:
                audio = AudioSegment.from_file(audio_path)
                cut_audio = audio[20*1000:20*1000+n_seconds * 1000]
                output_path = os.path.join(directory, f"cut_audio_{base}{ext}")
                cut_audio.export(output_path, format=ext[1:])
                print(f"Cut {filename} to {output_path}")
            except Exception as e:
                raise RuntimeError(f"Error processing {filename}: {e}")

def merge_cut_audio(directory, output_file):
    merged_audio = AudioSegment.empty()
    for filename in os.listdir(directory):
        if filename.startswith("cut_audio_") and filename.endswith(".mp3"):
            cut_audio_path = os.path.join(directory, filename)
            try:
                cut_audio = AudioSegment.from_file(cut_audio_path)
                merged_audio += cut_audio
                print(f"Added {filename} to the mashup")
            except Exception as e:
                raise RuntimeError(f"Error processing {filename}: {e}")

    try:
        output_path = os.path.join(directory, output_file)
        merged_audio.export(output_path, format="mp3")
        print("Mashup created successfully!")
    except Exception as e:
        raise RuntimeError(f"Error creating mashup: {e}")

def main():
    if len(sys.argv) != 5:
        raise InvalidInputError("Argument Missing\nUsage: python program_name.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
    
    singer_name = sys.argv[1]
    num_videos = int(sys.argv[2])
    audio_duration = int(sys.argv[3])
    output_file = sys.argv[4]

    if num_videos < 11:
        raise InvalidInputError("Number of videos must be at least 11")
    if audio_duration < 21:
        raise InvalidInputError("Audio duration must be at least 21 seconds")

    output_dir = os.path.join(os.getcwd(), "downloads")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Perform tasks
    video_links = get_youtube_video_links(singer_name, num_videos)
    download_youtube_videos(video_links, output_dir)
    convert_videos_to_audio(output_dir)
    cut_audio_files(audio_duration, output_dir)
    merge_cut_audio(output_dir, output_file)

if __name__ == "__main__":
    try:
        main()
    except (InvalidInputError, RuntimeError) as e:
        print(f"Error: {e}")
