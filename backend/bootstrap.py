"""Registra os subscribers de domínio (gamificação, mascote) no
despachante de `core.domain_events`.

Deve ser importado uma vez no processo — por `api/main.py` e pelos
`conftest.py` de teste que exercitam tools isoladas sem subir o app. O
import de cada módulo `*.subscribers` tem efeito colateral de chamar
`domain_events.subscribe(...)`; `subscribe` é idempotente, então importar
`bootstrap` mais de uma vez não duplica handlers.
"""

from gamification import subscribers as _gamification_subscribers  # noqa: F401
from mascot import subscribers as _mascot_subscribers  # noqa: F401
