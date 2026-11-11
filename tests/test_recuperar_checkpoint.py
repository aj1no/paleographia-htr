import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import recuperar_checkpoint as rc  # noqa: E402


def test_escolhe_maior_acerto_e_o_primeiro_no_empate(tmp_path):
    for nome in ("checkpoint_02-0.8656.ckpt", "checkpoint_03-0.8695.ckpt", "checkpoint_04-0.8695.ckpt",
                 "checkpoint_03-0.8695-v1.ckpt", "checkpoint_05-0.8667.ckpt", "outro.ckpt"):
        (tmp_path / nome).write_bytes(b"")
    assert rc.escolher(tmp_path).name == "checkpoint_03-0.8695.ckpt"


def test_sem_checkpoint_recusa(tmp_path):
    with pytest.raises(SystemExit):
        rc.escolher(tmp_path)


def test_treino_d_segura_o_101r_para_a_validacao():
    import treinar_ao_vivo
    pares = treinar_ao_vivo.pares("D")
    validacao = [p for p in pares if p["split"] == "validation"]
    assert {p["document_id"] for p in validacao} == {"sessao_1795", "jundiai_atas_sessao_1831-07-11"}
    assert all(p["folio"] == "f101r" for p in validacao if p["document_id"].startswith("jundiai"))
    assert not any(p["split"] == "train" and p.get("folio") == "f101r" and p["document_id"].startswith("jundiai")
                   for p in pares)
