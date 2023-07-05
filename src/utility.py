import math
import cv2
from moviepy.editor import VideoFileClip


def video_writer_from_cap(path, cap, fourcc='mp4v'):
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*fourcc)
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
    writer.set(cv2.VIDEOWRITER_PROP_QUALITY, 1.0)

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


def decompose_affine(affine):
    # https://frederic-wang.fr/decomposition-of-2d-transform-matrices.html
    # skew scale rotate translate
    [[a, c, e], [b, d, f]] = affine
    delta = a * d - b * c
    if a != 0 or b != 0:
        r = math.sqrt(a * a + b * b)
        rotation = math.acos(a / r) if b > 0 else -math.acos(a / r)
        scale = [r, delta / r]
        skew = [math.atan((a * c + b * d) / (r * r)), 0]
    elif c != 0 or d != 0:
        s = math.sqrt(c * c + d * d)
        rotation = math.pi / 2 - \
            (math.acos(-c / s) if d > 0 else -math.acos(c / s))
        scale = [delta / s, s]
        skew = [0, math.atan((a * c + b * d) / (s * s))]
    else:
        return [0, 0], [0, 0], 0, [0, 0]

    return skew, scale, rotation, [e, f]
