import json
from pyzbar import pyzbar

from .utility import decompose_affine
from .sift import SiftImage, sift_image_and_mask_from_png
import cv2
import numpy as np


def wrap_affine(image, matrix):
    shape = [image.shape[1], image.shape[0]]
    return cv2.warpAffine(image, matrix, shape)


def region_similarity(image1, image2, mask):
    def unify(image):
        image = image * mask.reshape([*image.shape[:2], 1])
        image = image / np.sum(image)
        return image
    return np.sum(np.minimum(unify(image1), unify(image2)))


def find_qrcode_rect_list(target: SiftImage):
    barcodes = pyzbar.decode(target.image)
    rects = []
    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        rects.append((x, y, w, h))
    return rects


class SiftQueryProcessor:

    def __init__(
        self, query: SiftImage, mask,
            min_match=5, knn_ratio=0.7, min_similarity=None,
            min_scale=None, max_scale=None,
            pre_frame_num=0, post_frame_num=0,
            max_translation=None, max_rotation=None,
            remove_features=True):

        self.matcher = cv2.BFMatcher()
        self.query = query
        self.mask = mask

        self.knn_matcher_ratio = knn_ratio
        self.min_match = min_match

        self.min_similarity = min_similarity

        self.min_scale = min_scale
        self.max_scale = max_scale
        self.max_translation = max_translation
        self.max_rotation = max_rotation

        self.pre_frame_num = pre_frame_num
        self.post_frame_num = post_frame_num

        self.remove_features = remove_features

    @staticmethod
    def from_config(config):
        query_config = config.get('query', {})
        query_path = query_config['path']
        image, query_mask = sift_image_and_mask_from_png(query_path)
        query_processor = SiftQueryProcessor(
            image, query_mask,
            min_match=query_config.get('min_match', 5),
            knn_ratio=query_config.get('knn_ratio', 0.5),
            min_similarity=query_config.get('min_similarity', None),
            min_scale=query_config.get('min_scale', None),
            max_scale=query_config.get('max_scale', None),
            max_rotation=query_config.get('max_rotation', None),
            max_translation=query_config.get('max_translation', None),
            pre_frame_num=query_config.get('pre_frame_num', 0),
            post_frame_num=query_config.get('post_frame_num', 0)
        )

        return query_processor

    def process(self, target: SiftImage):
        query = self.query
        matches = None
        if self.knn_matcher_ratio is not None:
            knn_matches = self.matcher.knnMatch(
                query.descriptors, target.descriptors, k=2)
            matches = [
                m for m, n in knn_matches
                if m.distance < self.knn_matcher_ratio*n.distance]
        else:
            matches = self.matcher.match(
                query.descriptors, target.descriptors)

        # check minimal number of matches
        if len(matches) < self.min_match:
            return None

        affine = self.query.estimate_affine(target, matches)
        skew, scale, rotation, translation = decompose_affine(affine)

        if self.min_scale is not None:
            if abs(scale[0]) < self.min_scale:
                return None
            if abs(scale[1]) < self.min_scale:
                return None

        if self.max_scale is not None:
            if abs(scale[0]) > self.max_scale:
                return None
            if abs(scale[1]) > self.max_scale:
                return None

        if self.max_rotation is not None:
            if abs(rotation) > self.max_rotation:
                return None

        if self.max_translation is not None:
            if abs(translation[0]) > self.max_translation:
                return None
            if abs(translation[1]) > self.max_translation:
                return None

        affine_query_image = self.query.wrap_affine(affine)
        affine_query_mask = wrap_affine(self.mask, affine)

        if self.min_similarity is not None:
            similarity = region_similarity(
                affine_query_image, target.image, affine_query_mask)
            if similarity < self.min_similarity:
                return None

        if self.remove_features:
            target.filter_features(affine_query_mask)

        return affine


DEFAULT_REMOVE_STRATEGY = 'INPAINT'
DEFAULT_INPAINT_RADIUS = 5


class QueryProcessors:

    def __init__(self, sift_query_list, qr_pre_frames, qr_post_frames):
        self.sift_query_list: list[SiftQueryProcessor] = sift_query_list
        self.qr_pre_frames = qr_pre_frames
        self.qr_post_frames = qr_post_frames

    @staticmethod
    def from_config(config):
        qrcode = config.get('qrcode', {})
        if qrcode == {}:
            print('qrcode config is not set, using default 25, 25.')
        return QueryProcessors(
            [SiftQueryProcessor.from_config(cfg) for cfg in config['image']],
            qrcode.get('pre_frame_num', 25),
            qrcode.get('post_frame_num', 25)
        )

    @staticmethod
    def from_config_path(path):
        with open(path) as f:
            config = json.load(f)
        return QueryProcessors.from_config(config)

    def process_video(self, cap, release=True):
        video_qr_rect = []
        video_affine = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()  # bgr
            if not ret:  # end of video
                break
            frame_count += 1
            print('query processing', frame_count, '/', total_frames, end='\r')

            target = SiftImage(frame)  # mutable

            video_qr_rect.append(find_qrcode_rect_list(target))
            frame_affine = []
            for sift_query in self.sift_query_list:
                query_affine = []
                # TODO: never seen repeated logo, modify for loop if request changed
                try:
                    affine = sift_query.process(target)
                    if affine is not None:
                        query_affine.append(affine)
                except Exception as e:
                    print('caught_error when query: ', e)
                    print('error image written')
                    cv2.imwrite(
                        f'./errorFrame/error_{frame_count}.jpg', target.image)
                frame_affine.append(query_affine)
            video_affine.append(frame_affine)
        print()

        if release:
            cap.release()

        video_affine_aug = {}

        for frame_id, frame_affine in enumerate(video_affine):
            print(
                f'filling pre-post-frame {frame_id+1} / {len(video_affine)}', end='\r')
            for query_id, query_affine in enumerate(frame_affine):
                if len(query_affine) == 0:
                    continue
                sift_query = self.sift_query_list[query_id]
                begin = max(0, frame_id-sift_query.pre_frame_num)
                end = min(frame_id+sift_query.post_frame_num,
                          len(video_affine))
                for to_frame_id in range(begin, end):
                    if len(video_affine[to_frame_id][query_id]) == 0 and \
                            len(video_affine_aug.get((to_frame_id, query_id), [])) == 0:
                        video_affine_aug[(to_frame_id, query_id)
                                         ] = query_affine

        for (to_frame_id, query_id), query_affine in video_affine_aug.items():
            video_affine[to_frame_id][query_id] = query_affine

        video_qr_rect_aug = {}

        print()
        for frame_id, frame_qr_rect in enumerate(video_qr_rect):
            print(
                f'filling pre-post-frame {frame_id+1} / {len(video_qr_rect)}', end='\r')
            if len(frame_qr_rect) == 0:
                continue
            begin = max(0, frame_id-self.qr_pre_frames)
            end = min(frame_id+self.qr_post_frames, len(video_qr_rect))
            for to_frame_id in range(begin, end):
                if len(video_qr_rect[to_frame_id]) == 0 and \
                        len(video_qr_rect_aug.get(to_frame_id, [])) == 0:
                    video_qr_rect_aug[to_frame_id] = frame_qr_rect
        print()

        for to_frame_id, frame_qr_rect in video_qr_rect_aug.items():
            video_qr_rect[to_frame_id] = frame_qr_rect

        return video_affine, video_qr_rect
