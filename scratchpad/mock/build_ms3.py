# Assemble ms3.py from its pieces (kept apart so each can be rewritten without retyping the rest).
parts = [open(n).read() for n in ('ms3_head.txt', 'ms3_body.txt', 'ms3_tail.txt')]
open('ms3.py', 'w').write('\n'.join(p.rstrip('\n') + '\n' for p in parts))
