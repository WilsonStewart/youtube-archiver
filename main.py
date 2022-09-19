import json
from pytube import Channel
from os.path import exists

version = "0.1.0"

print(f"||Youtube Archiver v{version}")
print("")

# Import archive_channels.json file
with open("archive_channels.json") as archive_channels_file:
    archive_channels_config = json.load(archive_channels_file)

print("Parsing channels config...")
number_of_channels = len(archive_channels_config)
print(f"-> Found {number_of_channels} channels to archive!")

for channel_id in archive_channels_config:

    # Create channel  file if it does not exist
    if not exists(f"channels/{channel_id}.json"):
        emptyChannelData = {
            "id": channel_id,
            "name": "",
            "description": "",
            "videos_archived": [],
        }

        with open(f"channels/{channel_id}.json", "w") as channel_file:
            json.dump(emptyChannelData, channel_file)

    # Load channel data from disk
    with open(f"channels/{channel_id}.json") as channel_data_file:
        channel_data = json.load(channel_data_file)

    print(f"Archiving {channel_data['id']}")

    # Create the pytube channel object
    channel_obj = Channel(f"https://youtube.com/c/{channel_data['id']}")

    # Update the metadata in the channel_data
    # channel_data["name"] = channel_obj.channel_name
    # channel_data["description"] = channel_obj.description

    # Get a list of already downloaded files, to exclude from download again.
    exclusion_list = []
    for video in channel_data["videos_archived"]:
        exclusion_list.append(video["id"])

    for video in channel_obj.videos:

        # Load channel data from disk
        with open(f"channels/{channel_id}.json") as channel_data_file:
            channel_data = json.load(channel_data_file)

        # Skip the video if it's already been archived.
        if video.video_id in exclusion_list:
            print(f"-> Skipping {video.title}")

        # Otherwise, archive it
        else:
            print(f"-> Downloading {video.title}")

            video_data = {
                "id": video.video_id,
                "title": video.title,
                "date": (video.publish_date.isoformat())[0:10],  # type: ignore
                "description": video.description,
            }

            channel_data["videos_archived"].append(video_data)

            # Download video
            filename = f"{channel_data['id']} - {video_data['date']} {video.title} [youtube-{video.video_id}]"  # type: ignore
            video.streams.get_highest_resolution().download(f"channels/{channel_data['id']}/", f"{filename}.mp4")  # type: ignore

            exclusion_list.append(video.video_id)

            with open(f"channels/{channel_id}.json", "w") as channel_data_file:
                json.dump(channel_data, channel_data_file, default=str)
