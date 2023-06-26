import json
from .query import QueryProcessors, wrap_affine
from .sift import SiftImage, image_and_mask_from_png, sift_image_and_mask_from_png
import numpy as np
import cv2


DEFAULT_BLUR_RADIUS = 3


def blur(image, mask):
    l = int(np.sum(mask)**0.5/20)
    mask = mask.reshape([*mask.shape, 1])
    blur_image = cv2.blur(image, [l, l])
    return blur_image * mask+image * (1-mask)


class RemoveProcessor:

    def __init__(
            self, strategy,
            inpaint_mask=None, inpaint_radius=None, cover_image=None, cover_mask=None):

        self.strategy = strategy
        if strategy == 'INPAINT':
            self.inpaint_radius = inpaint_radius
            self.inpaint_mask = inpaint_mask
        elif strategy == 'COVER':
            self.cover_image = cover_image
            self.cover_mask = cover_mask
        else:
            raise Exception('COVER or INPAINT')

    @staticmethod
    def from_config(config):
        DEFAULT_REMOVE_STRATEGY = 'INPAINT'
        DEFAULT_INPAINT_RADIUS = 3
        query_config = config.get('query', {})
        query_path = query_config['path']
        image, query_mask = sift_image_and_mask_from_png(query_path)
        remove_config = config.get('remove', {})
        strategy = remove_config.get('strategy', DEFAULT_REMOVE_STRATEGY)
        if strategy == 'INPAINT':
            radius = remove_config.get(
                'inpaint_radius', DEFAULT_INPAINT_RADIUS)
            remove_processor = RemoveProcessor(
                strategy, inpaint_mask=query_mask, inpaint_radius=radius)
        elif strategy == 'COVER':
            image, cover_mask = image_and_mask_from_png(remove_config['path'])
            remove_processor = RemoveProcessor(
                strategy, cover_image=image, cover_mask=cover_mask)
        return remove_processor

    def process_inpaint(self, image, affine):
        mask = wrap_affine(self.inpaint_mask, affine)
        return cv2.inpaint(image, mask, self.inpaint_radius, cv2.INPAINT_TELEA)

    def process_cover(self, image, affine):
        mask = wrap_affine(self.cover_mask, affine)[:, :, np.newaxis]
        cover = wrap_affine(self.cover_image, affine)
        return (image * (1 - mask)) + (cover * mask)

    def process(self, target, affine):
        if self.strategy == 'INPAINT':
            target = self.process_inpaint(target, affine)
            mask = wrap_affine(self.inpaint_mask, affine)
            target = blur(target, mask)
        if self.strategy == 'COVER':
            target = self.process_cover(target, affine)
            mask = wrap_affine(self.cover_mask, affine)
        return target


def rect_to_mask(rect, shape, dilation=10):
    (x, y, w, h) = rect
    mask = np.zeros(shape, dtype=np.uint8)
    y_l = max(0, y-dilation)
    y_h = min(y+h+dilation, shape[0])
    x_l = max(0, x-dilation)
    x_h = min(x+w+dilation, shape[1])
    mask[y_l:y_h, x_l:x_h] = 1
    return mask


class RemoveProcessors:

    def __init__(self, remove_processors) -> None:
        self.remove_processors: list[RemoveProcessor] = remove_processors

    @staticmethod
    def from_config(config):
        return RemoveProcessors([RemoveProcessor.from_config(cfg) for cfg in config['image']])

    @staticmethod
    def from_config_path(path):
        with open(path) as f:
            config = json.load(f)
        return RemoveProcessors.from_config(config)

    def process_image(self, target, frame_affine, qr_rects):
        for pid, remove_affine in enumerate(frame_affine):
            for affine in remove_affine:
                target = self.remove_processors[pid].process(target, affine)
        QR_INPAINT_RADIUS = 3
        for qr_rect in qr_rects:
            qr_mask = rect_to_mask(qr_rect, target.shape[:2])
            target = cv2.inpaint(
                target, qr_mask, QR_INPAINT_RADIUS, cv2.INPAINT_TELEA)
        return target

    def process_cap(self, writer, cap, video_affine, qr_rectss, release=True):
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_id = 0
        while cap.isOpened():
            ret, frame = cap.read()  # bgr
            if not ret:  # end of video
                break
            print('remove processing', frame_id +
                  1, '/', total_frames, end='\r')

            qr_rects = qr_rectss[frame_id]
            frame_affine = video_affine[frame_id]
            output = self.process_image(frame, frame_affine, qr_rects)
            writer.write(output)
            frame_id += 1
        print()
        if release:
            cap.release()
            writer.release()
