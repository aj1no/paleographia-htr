"""Proteções operacionais do recálculo acadêmico; ativadas por sitecustomize."""
import ipaddress
import json
import os
import shlex
import socket
import sys
from pathlib import Path


def instalar():
    root = Path(os.environ['PALEOGRAPHIA_CI_ROOT']).resolve()
    log = Path(os.environ['PALEOGRAPHIA_CI_LOG']).resolve()
    allowed = [root/'output', root/'tmp']
    forbidden = ('torch', 'torchvision', 'transformers', 'onnxruntime', 'kraken',
                 'paddle', 'paddleocr', 'paleographia.recognition', 'paleographia.backends',
                 'paleographia.kraken_recognition', 'paleographia.latin_ocr',
                 'paleographia.training', 'paleographia.services', 'paleographia.api',
                 'paleographia.segmentation')

    def record(event, **details):
        with log.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'evento': event, 'pid': os.getpid(), **details}, ensure_ascii=True)+'\n')

    def deny(reason, target):
        record('bloqueado', motivo=reason, alvo=str(target))
        raise RuntimeError('CI acadêmica bloqueou '+reason+': '+str(target))

    class NoRecognition:
        def find_spec(self, fullname, path=None, target=None):
            if any(fullname == name or fullname.startswith(name+'.') for name in forbidden):
                deny('importacao_de_inferencia', fullname)

    def local(host):
        if isinstance(host, (tuple, list)):
            host = host[0]
        if host in (None, '', 'localhost', b'localhost'):
            return True
        try:
            return ipaddress.ip_address(os.fsdecode(host)).is_loopback
        except ValueError:
            return False

    def protected(path):
        if isinstance(path, int) or path is None:
            return False
        path = Path(os.fsdecode(path)).resolve()
        return path.is_relative_to(root) and not any(path.is_relative_to(p) for p in allowed)

    def audit(event, args):
        if event == 'socket.getaddrinfo' and not local(args[0]):
            deny('conexao_externa', args[0])
        if event == 'socket.connect' and args[0].family != getattr(socket, 'AF_UNIX', None) and not local(args[1]):
            deny('conexao_externa', args[1])
        if event == 'subprocess.Popen':
            command = args[1]
            # O Python publica a linha já serializada no evento do Windows.
            if isinstance(command, str) and os.name == 'nt':
                command = [part.strip('"') for part in shlex.split(command, posix=False)]
            kernel = (isinstance(command, (list, tuple)) and len(command) == 5
                      and Path(command[0]).resolve() == Path(sys.executable).resolve()
                      and list(command[1:4]) == ['-m', 'ipykernel_launcher', '-f'])
            font = isinstance(command, (list, tuple)) and Path(command[0]).name in {'fc-list', 'fc-match'}
            cpu_info = (isinstance(command, (list, tuple)) and len(command) == 2
                        and Path(command[0]).name == 'uname' and command[1] == '-p')
            if not (kernel or font or cpu_info):
                deny('subprocesso_nao_autorizado', command)
        if event == 'open':
            path, mode, flags = args
            if not isinstance(path, int) and Path(os.fsdecode(path)).resolve().is_relative_to(root/'models'):
                deny('acesso_a_pesos', path)
            writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(
                flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing and protected(path):
                deny('escrita_em_entrada', path)
        if event in {'os.mkdir', 'os.remove', 'os.rmdir', 'os.rename'}:
            paths = args[:2] if event == 'os.rename' else args[:1]
            for path in paths:
                if protected(path):
                    deny('alteracao_de_entrada', path)

    for name in tuple(sys.modules):
        if any(name == prefix or name.startswith(prefix+'.') for prefix in forbidden):
            deny('modulo_de_inferencia_precarregado', name)
    sys.meta_path.insert(0, NoRecognition())
    sys.addaudithook(audit)
    record('protecao_ativa', kernel='ipykernel_launcher' in getattr(sys, 'orig_argv', []))


if os.environ.get('PALEOGRAPHIA_CI_ROOT'):
    instalar()
