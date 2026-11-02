# Laboratoire synthétique — règles impératives

- Ce dépôt est **PUBLIC**. N'y introduire AUCUN code privé, secret, jeton, identifiant, extrait de log sensible ou configuration des projets SKZTOUCH.
- Claude Code est l'**implémenteur**; Codex est le **réviseur indépendant**.
- Ne modifier que `mathops.py`, sur une branche de travail issue de `pilot/lot-b-synthetic-fixture`.
- Les tests, le contrat, les workflows et les règles de sécurité sont immuables pour les agents.
- Aucune écriture directe sur `main`, aucun merge, aucun auto-merge, aucun déploiement.
- Les agents ne doivent avoir ni autorisation de merge ni credentials d'écriture sur les dépôts de production.
- Révision Codex sur le SHA de code réel, distinct de la session Claude. CI GitHub green obligatoire.
- HUMAN_GATE après ouverture de draft PR : le propriétaire décide.
- **Arrêt avant toute exécution réelle** tant que l'issue SKZTOUCH/orchestrator-os#9 n'atteste pas que `main` est protégée et que les identités sont isolées.
