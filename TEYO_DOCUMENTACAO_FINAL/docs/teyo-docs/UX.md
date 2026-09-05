# UX.md

## Princípios (DECIDIDO, doc. 3, item 44)

- Simples, prático, rápido, amigável.
- Não transformar cada ação em formulário complexo quando a conversa resolve.
- Quando uma ação puder ser feita naturalmente pela conversa, o usuário deve poder usar a conversa em vez de navegar por telas.

## Estados de tela (NECESSÁRIO PARA IMPLEMENTAÇÃO)

Toda tela de módulo deve prever, no mínimo:
- **Loading**: enquanto dados são buscados do backend.
- **Vazio**: quando não há dados ainda (ex.: nenhuma tarefa cadastrada) — deve orientar o usuário a criar o primeiro item, inclusive sugerindo fazer isso conversando com o TEYO.
- **Erro**: falha ao carregar/salvar — ver `ERROR_HANDLING.md`.
- **Sucesso**: confirmação visual de ação concluída (ex.: tarefa marcada como concluída).

## Modais e formulários

- Ações destrutivas (excluir tarefa/compromisso/item) sempre passam por confirmação, seja na tela (modal) seja na conversa (pergunta do TEYO) — regra 4 de `BUSINESS_RULES.md`.
- Formulários de criação/edição existem como alternativa à conversa, não como via obrigatória.

## Identidade visual

DECIDIDO: existe uma referência visual já criada para o conceito do TEYO (dashboard, progresso, conquistas, mascote, mensagens motivacionais, cards). NECESSÁRIO PARA IMPLEMENTAÇÃO: essa referência deve ser tratada como inspiração visual/conceitual, respeitando as restrições já decididas (cor do mascote customizável; sem acessórios livres; expressões e evolução controladas pelo sistema). A DEFINIR: assets visuais finais (ainda não entregues a esta documentação).

## Responsividade

A DEFINIR: breakpoints exatos. DECIDIDO: produto é web/PWA, deve funcionar em desktop (Mac) e mobile (iPhone/Android) — ver `/topics/tools.md` do usuário para contexto de dispositivos.

## Tom das mensagens do sistema (DECIDIDO, doc. 3, item 45 — exemplos de referência, não texto obrigatório)

- "Você concluiu 3 tarefas importantes hoje. Orgulho define!"
- "Ei, tudo bem fazer uma pausa."
- "Pequenos passos te levam longe."
- "Foco hoje, liberdade amanhã."
- "Descansar também é produtividade."

Essas frases são referência de tom para o Claude Code escrever variações, não strings fixas obrigatórias no código.
