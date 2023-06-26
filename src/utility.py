import cv2
from moviepy.editor import VideoFileClip


def video_writer_from_cap(path, cap, fourcc='RGBA'):
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*fourcc)
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))

    return writer


def add_audio_to_video(
    silent_video_path, input_video_path, output_video_path,
        bitrate='4000k'):
    silent_video = VideoFileClip(silent_video_path)
    input_video = VideoFileClip(input_video_path)
    audio = input_video.audio
    video = silent_video.set_audio(audio)
    video.write_videofile(
        output_video_path,
        bitrate=bitrate,
        audio_codec="aac",
        codec="libx264"
    )

    input_video.close()
    silent_video.close()
    video.close()
    return audio
