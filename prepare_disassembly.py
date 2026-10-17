"""Generate disassembler symbols from SMK's SH68F90 register definitions."""
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
header = (root / 'smk/src/sino51lib/sh68f90/sh68f90.h').read_text()
symbols = ['RESET CODE 0000h']
for name, addr in re.findall(r'^SFR\((\w+), (0x[0-9a-fA-F]+)\);', header, re.M):
    symbols.append(f'{name} DATA {int(addr, 16):04X}h')
for name, addr, bit in re.findall(r'^SBIT\((\w+), (0x[0-9a-fA-F]+), (\d+)\);', header, re.M):
    symbols.append(f'{name} BIT {int(addr, 16) + int(bit):04X}h')
(root / 'sh68f90.mcu').write_text('\n'.join(symbols) + '\n')
cmd = [str(root / 'venv/bin/disasm51'), '--include', str(root / 'sh68f90.mcu'), '--entry', 'RESET']
for addr in range(3, 0x7c, 8):
    cmd.extend(['--entry', hex(addr)])
# Computed-jump table discovered in the stock matrix scan routine.
cmd.extend(['--entry', '0x9493:0x94bd:3'])
cmd.append(str(root / 'stock-full-isp.bin'))
with (root / 'stock.asm').open('w') as out:
    subprocess.run(cmd, stdout=out, check=True)
