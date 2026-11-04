"""Roda inferência Kraken em recortes sem acesso às referências."""
import hashlib
import json
from pathlib import Path

import torch
from PIL import Image
from kraken.configs import RecognitionInferenceConfig
from kraken.lib.dataset import ImageInputTransforms
from kraken.tasks import RecognitionTaskModel


def single(folder, pattern):
    paths = list(folder.glob(pattern))
    if len(paths) != 1:
        raise ValueError(f"Esperado um arquivo {pattern} em {folder}.")
    return paths[0]


def main():
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    images = sorted(Path("/images").glob("*.png"))
    if len(images) != 10:
        raise ValueError("Esperados os dez recortes reservados no piloto.")
    config = RecognitionInferenceConfig(
        accelerator="cpu", device=1, precision="32-true",
        batch_size=1, num_line_workers=0, padding=16, bidi_reordering=False,
    )
    result = {}
    common_layout = None
    for name in ("zero", "pretreino"):
        folder = Path("/models") / name / "extended"
        weights = single(folder, "*.safetensors")
        checkpoint_path = single(folder, "checkpoint_74-*.ckpt")
        checkpoint = torch.load(checkpoint_path, weights_only=False, map_location="cpu")
        if (checkpoint["epoch"], checkpoint["global_step"]) != (74, 451):
            raise ValueError("O checkpoint precisa corresponder ao fim do treino fixado.")
        net = RecognitionTaskModel.load_model(weights).net
        if type(net).__name__ != "TorchVGSLModel" or net.seg_type != "baselines":
            raise ValueError("Modelo ou tipo de faixa divergente.")
        layout = (net.spec, tuple(net.input), net.codec.c2l)
        if common_layout is None:
            common_layout = layout
        elif layout != common_layout:
            raise ValueError("A arquitetura ou o alfabeto dos dois modelos diverge.")
        net.prepare_for_inference(config)
        batch, channels, height, width = net.input
        transform = ImageInputTransforms(batch, height, width, channels, (16, 0), False, dtype=net._m_dtype)
        lines = []
        with torch.inference_mode():
            for path in images:
                with Image.open(path) as opened:
                    tensor = transform(opened.convert("L")).unsqueeze(0)
                decoded, _ = net._rec_predict(tensor, torch.LongTensor([tensor.shape[-1]]))
                lines.append({
                    "line_id": path.stem, "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "text_raw": "".join(item[0] for item in decoded[0]),
                })
        result[name] = {
            "weights": weights.relative_to("/models").as_posix(),
            "weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
            "checkpoint": checkpoint_path.relative_to("/models").as_posix(),
            "epoch": 75, "optimizer_steps": checkpoint["global_step"], "lines": lines,
        }
    output = Path("/predictions/predictions.json")
    with output.open("x", encoding="utf-8") as stream:
        json.dump({"models": result, "vgsl_spec": common_layout[0],
                   "model_input": list(common_layout[1]), "codec": common_layout[2],
                   "decoding": "Kraken greedy CTC", "horizontal_padding": 16}, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
