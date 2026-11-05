"""Fine-tuning data export without Docker: reserved test refused, augmentation only in train."""
import pytest
from PIL import Image

from paleographia.ppocrv6_finetune import augment_variants, prepare


def crop(tmp_path, name):
    path = tmp_path / "crops" / name
    path.parent.mkdir(exist_ok=True)
    Image.new("RGB", (300, 40), (235, 225, 200)).save(path)
    return "crops/" + name


def test_reserved_test_document_never_reaches_training(tmp_path):
    pairs = [{"crop_image": crop(tmp_path, "a.png"), "text": "Aos vinte", "document_id": "pagamento_thomas_pardo",
              "split": "train"}]
    with pytest.raises(ValueError, match="Teste reservado"):
        prepare(pairs, tmp_path / "run", tmp_path)


def test_prepare_writes_ketos_pairs_and_augments_only_training(tmp_path):
    pairs = [{"crop_image": crop(tmp_path, "a.png"), "text": "Aos vinte", "document_id": "doc_a", "split": "train"},
             {"crop_image": crop(tmp_path, "b.png"), "text": "de junho", "document_id": "doc_b", "split": "validation"}]
    evidence, counts = prepare(pairs, tmp_path / "run", tmp_path, augment=2)
    assert counts == {"train": 3, "validation": 1}
    gt = sorted((tmp_path / "run/data/train").glob("*.gt.txt"))
    assert len(gt) == 3 and all(p.read_text(encoding="utf-8") == "Aos vinte" for p in gt)
    assert (tmp_path / "run/data/validation.lst").read_text().strip().endswith(".png")
    assert evidence[0]["variants"] == 3 and evidence[1]["variants"] == 1


def test_augment_variants_keep_line_shape():
    import random
    image = Image.new("RGB", (400, 50), (230, 220, 200))
    for variant in augment_variants(image, 5, random.Random(1)):
        assert variant.mode == "RGB" and variant.width > 3 * variant.height


def test_per_pair_augment_override_balances_sources(tmp_path):
    pairs = [{"crop_image": crop(tmp_path, "a.png"), "text": "local", "document_id": "doc_a", "split": "train", "augment": 2},
             {"crop_image": crop(tmp_path, "b.png"), "text": "externo", "document_id": "doc_b", "split": "train", "augment": 0},
             {"crop_image": crop(tmp_path, "c.png"), "text": "val", "document_id": "doc_c", "split": "validation"}]
    _, counts = prepare(pairs, tmp_path / "run", tmp_path, augment=5)
    assert counts == {"train": 4, "validation": 1}
