# BUSINESS_RULES.md

Lista consolidada de regras de negócio extraídas do histórico e do briefing de documentação. Todas DECIDIDAS, salvo indicação contrária.

1. Uma tarefa única não vira recorrente automaticamente.
2. Uma mudança isolada de comportamento não altera uma rotina aprendida; rotina só muda após observação sustentada (ver `PATTERN_ENGINE.md`).
3. Padrões precisam de observação ao longo de uma janela de tempo antes de virarem "ativos"; nenhum padrão é criado a partir de um único evento.
4. Ações destrutivas (excluir tarefa, excluir compromisso, excluir item) exigem confirmação explícita do usuário antes da execução da tool correspondente.
5. Ações ambíguas (ex.: mais de uma tarefa possível para "essa tarefa") exigem esclarecimento do usuário antes da execução.
6. O LLM não inventa dados: números, datas, tarefas ou fatos sobre o usuário sempre vêm do sistema.
7. Cálculos (financeiros, de produtividade, de XP, de padrões) pertencem ao sistema, nunca ao LLM.
8. O LLM não afirma que executou uma ação sem ter recebido confirmação de sucesso da tool correspondente.
9. Pomodoro é opcional em qualquer tarefa; nenhuma tarefa exige Pomodoro.
10. O mascote não é livremente personalizável: apenas a cor pode ser alterada pelo usuário; expressões e evolução são controladas pelo sistema.
11. Não existe módulo de pets — removido explicitamente do escopo do produto.
12. O planejador sugere reorganizações; não aplica mudanças de agenda/tarefas em massa sem confirmação do usuário.
13. O TEYO não é autoridade sobre a vida do usuário: ele sugere, o usuário decide.
14. Quando o TEYO não tem informação suficiente para executar uma ação, ele pergunta em vez de assumir um valor.
15. Quando não souber a resposta, o TEYO admite que não sabe, em vez de inventar.
16. Regras do sistema têm precedência sobre qualquer interpretação do LLM — o LLM deve respeitar as regras definidas nesta documentação.
17. Notícias, preferências, memória e padrões são isolados por `user_id`, mesmo com um único usuário ativo no V1.
18. Nenhuma funcionalidade listada como FORA DO V1 em `V1_SCOPE.md` deve ser implementada nesta versão.
19. Dados do usuário podem ser controlados, alterados e removidos por ele (memória e preferências).
20. Uma única conversa principal com o TEYO; não existem chats separados por assunto.
