# ERROR_HANDLING.md

| Situação | Comportamento definido |
|---|---|
| LLM indisponível | TEYO UI mostra estado de erro explícito ao usuário (ex.: "não consegui processar agora"); nenhuma ação é executada; nenhuma resposta fingindo sucesso. |
| Modelo carregando | UI mostra estado de loading; requisições ficam na fila ou retornam erro de "tente novamente em instantes" (NECESSÁRIO PARA IMPLEMENTAÇÃO: decidir fila vs. rejeição imediata — A DEFINIR). |
| Tool falha | Orquestrador recebe erro da tool, repassa ao LLM como resultado de erro (não como sucesso); LLM informa ao usuário que a ação não foi concluída, sem inventar motivo técnico. |
| Banco indisponível | Erro 5xx propagado ao frontend; UI mostra estado de erro; nenhuma escrita parcial é assumida como concluída. |
| Resposta do LLM inválida (JSON malformado) | Adapter rejeita a resposta; Orquestrador trata como erro de geração, pode tentar nova geração (número de tentativas A DEFINIR) antes de informar erro ao usuário. |
| Ferramenta inexistente chamada pelo LLM | Orquestrador rejeita a chamada, não executa nada, loga o evento como anomalia; resposta ao usuário não confirma nenhuma ação. |
| Parâmetros obrigatórios ausentes | Tool não executa; Orquestrador direciona o LLM a perguntar o dado faltante ao usuário (regra 14 de `BUSINESS_RULES.md`). |
| Usuário cancela ação em andamento (ex.: recusa confirmação) | Nenhuma tool destrutiva/impactante é chamada; sistema mantém estado anterior. |
| Operação falha após confirmação do usuário | UI/conversa informa a falha explicitamente; não assume sucesso silencioso. |

## Princípio geral (DECIDIDO)

O TEYO nunca comunica ao usuário que uma ação foi concluída sem confirmação de sucesso vinda do sistema. Diante de erro, ambiguidade ou falta de informação, o TEYO pergunta, esclarece ou informa a falha — nunca assume ou inventa (regra de ouro, doc. 3, item 49).
