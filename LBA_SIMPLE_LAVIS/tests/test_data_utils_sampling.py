import ast
import pathlib
import unittest


DATA_UTILS = pathlib.Path(__file__).parents[1] / "lavis" / "datasets" / "data_utils.py"
SAMPLING_FUNCTIONS = {
    "_open_video",
    "_sample_frame_indices",
    "_read_video_frames",
    "_frames_to_tensor",
    "uniform_frame_sampling",
    "head_tail_frame_sampling",
    "load_clip",
}


class FakeFrame:
    def __init__(self, shape):
        self.shape = shape


class FakeTensor:
    def __init__(self, shape):
        self.shape = tuple(shape)

    def permute(self, *dims):
        return FakeTensor(tuple(self.shape[index] for index in dims))

    def float(self):
        return self


class FakeTorch:
    @staticmethod
    def tensor(frame):
        return FakeTensor(frame.shape)

    @staticmethod
    def stack(tensors, dim=0):
        shape = list(tensors[0].shape)
        shape.insert(dim, len(tensors))
        return FakeTensor(shape)


class FakeCapture:
    def __init__(self, opened=True, total_frames=4, fps=2.0, failed_indices=()):
        self.opened = opened
        self.total_frames = total_frames
        self.fps = fps
        self.failed_indices = set(failed_indices)
        self.position = 0
        self.positions = []

    def isOpened(self):
        return self.opened

    def get(self, prop):
        if prop == FakeCV2.CAP_PROP_FRAME_COUNT:
            return self.total_frames
        if prop == FakeCV2.CAP_PROP_FPS:
            return self.fps
        raise AssertionError(f"unexpected property: {prop}")

    def set(self, prop, value):
        if prop != FakeCV2.CAP_PROP_POS_FRAMES:
            raise AssertionError(f"unexpected property: {prop}")
        self.position = int(value)
        self.positions.append(self.position)

    def read(self):
        valid = 0 <= self.position < self.total_frames
        if not valid or self.position in self.failed_indices:
            return False, None
        return True, FakeFrame((4, 5, 3))

    def release(self):
        pass


class FakeCV2:
    CAP_PROP_FRAME_COUNT = 1
    CAP_PROP_FPS = 2
    CAP_PROP_POS_FRAMES = 3

    def __init__(self, captures):
        self.captures = captures

    def VideoCapture(self, path):
        return self.captures[path]

    @staticmethod
    def resize(frame, size):
        width, height = size
        return FakeFrame((height, width, frame.shape[2]))


def load_sampling_functions(fake_cv2):
    tree = ast.parse(DATA_UTILS.read_text())
    body = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in SAMPLING_FUNCTIONS
    ]
    namespace = {"cv2": fake_cv2, "torch": FakeTorch}
    exec(compile(ast.Module(body=body, type_ignores=[]), DATA_UTILS, "exec"), namespace)
    return namespace


class VideoSamplingTest(unittest.TestCase):
    def assert_clip_shape(self, function_name, capture, num_frames, **kwargs):
        functions = load_sampling_functions(FakeCV2({"video": capture}))
        clip = functions[function_name](
            "video",
            num_frames=num_frames,
            target_height=8,
            target_width=6,
            **kwargs,
        )
        self.assertEqual(clip.shape, (3, num_frames, 8, 6))
        self.assertEqual(len(capture.positions), num_frames)

    def test_short_clip_is_padded_with_duplicate_indices(self):
        for function_name in ("uniform_frame_sampling", "head_tail_frame_sampling"):
            with self.subTest(function_name=function_name):
                self.assert_clip_shape(
                    function_name,
                    FakeCapture(total_frames=2, fps=10.0),
                    num_frames=5,
                )

    def test_single_frame_request_has_exact_time_dimension(self):
        for function_name in ("uniform_frame_sampling", "head_tail_frame_sampling"):
            with self.subTest(function_name=function_name):
                self.assert_clip_shape(
                    function_name,
                    FakeCapture(total_frames=4, fps=2.0),
                    num_frames=1,
                )

    def test_time_boundaries_are_clamped_to_available_frames(self):
        capture = FakeCapture(total_frames=4, fps=2.0)
        self.assert_clip_shape(
            "uniform_frame_sampling",
            capture,
            num_frames=6,
            start_time=-10,
            end_time=100,
        )
        self.assertTrue(all(0 <= index <= 3 for index in capture.positions))
        self.assertEqual(capture.positions[0], 0)
        self.assertEqual(capture.positions[-1], 3)

    def test_invalid_video_metadata_and_reads_raise_value_error(self):
        invalid_captures = (
            FakeCapture(opened=False),
            FakeCapture(total_frames=0),
            FakeCapture(fps=0),
            FakeCapture(failed_indices={0}),
        )
        for capture in invalid_captures:
            with self.subTest(capture=capture):
                functions = load_sampling_functions(FakeCV2({"video": capture}))
                with self.assertRaises(ValueError):
                    functions["load_clip"](
                        "video",
                        num_frames=2,
                        target_height=8,
                        target_width=6,
                    )

    def test_non_positive_num_frames_is_rejected(self):
        functions = load_sampling_functions(
            FakeCV2({"video": FakeCapture(total_frames=4, fps=2.0)})
        )
        with self.assertRaisesRegex(ValueError, "num_frames"):
            functions["load_clip"](
                "video",
                num_frames=0,
                target_height=8,
                target_width=6,
            )


if __name__ == "__main__":
    unittest.main()
