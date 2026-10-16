import numpy as np
import pytest
from PIL import Image

from paleographia.latin_ocr import LatinONNXRecognizer, decode_ctc, prepare_pixels


def test_ctc_preserves_unicode_case_and_blank_separated_repeats():
    characters = ["blank", "á", "D", " ", ","]
    ids = [0, 1, 1, 0, 1, 3, 3, 2, 4, 4, 0]
    scores = np.eye(len(characters), dtype=np.float32)[ids][None]
    text, tokens = decode_ctc(scores, characters)
    assert text == "áá D,"
    assert tokens == ids
    assert decode_ctc(np.eye(5)[[0, 0]][None], characters)[0] == ""


def test_ctc_rejects_wrong_dictionary_and_nonfinite_values():
    with pytest.raises(ValueError, match="dicionário"):
        decode_ctc(np.zeros((1, 4, 3)), ["blank", "a"])
    with pytest.raises(ValueError, match="não finitos"):
        decode_ctc(np.full((1, 4, 2), np.nan), ["blank", "a"])


def test_native_preprocessing_channel_order_padding_and_long_line():
    image = Image.new("RGB", (48, 48), (255, 0, 0))
    pixels = prepare_pixels(image)
    assert pixels.shape == (1, 3, 48, 320)
    assert pixels.dtype == np.float32
    np.testing.assert_array_equal(pixels[0, :, 0, 0], [-1, -1, 1])
    assert not pixels[:, :, :, 48:].any()
    assert prepare_pixels(Image.new("RGB", (1000, 50))).shape == (1, 3, 48, 960)


def test_model_digest_failure_is_explicit_before_loading_optional_engine(tmp_path):
    path = tmp_path/"model.onnx"
    path.write_bytes(b"wrong model")
    recognizer = LatinONNXRecognizer(path)
    with pytest.raises(ValueError, match="Hash"):
        recognizer.load()
    assert recognizer.status()["state"] == "unavailable"
    assert recognizer.session is None
