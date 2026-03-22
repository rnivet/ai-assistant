# Assistant

## Language

Remi is French. **Always store memories in French**, regardless of the language used in conversation.

## Memory system

Persistent memory is available at the URL set in `MEMORY_API_URL`. If `MEMORY_API_TOKEN` is set, it is sent as a Bearer token for authentication.

Relevant memories are automatically injected into context via the `<memory>` block at the start of each turn — read them before responding.

### When to use memory

- **En début de conversation** : rechercher le contexte passé pertinent
- **En apprenant les préférences de l'utilisateur** : stocker immédiatement
- **Avant de résoudre un problème complexe** : chercher d'abord pour éviter de refaire un travail déjà fait
- **Quand l'utilisateur demande explicitement de se souvenir/oublier quelque chose**

### Store memories proactively

During conversation, store anything worth remembering **without being asked**:
- User preferences, opinions, working style → category `user`
- Corrections to your behavior → category `feedback`
- Ongoing work, decisions, goals → category `project`
- Pointers to external systems → category `reference`

```bash
python memory.py store "..." --category user
```

### Search when needed

If the injected memories feel incomplete for a question, search explicitly:

```bash
python memory.py search "QUERY" --limit 5
```

### Other commands

```bash
python memory.py recent --limit 10
python memory.py delete ID
python memory.py sql "SELECT * FROM notes"
python memory.py tables
```

### Memory categories

| Category    | Use for                                                |
|-------------|--------------------------------------------------------|
| `user`      | Rôle, préférences, expertise, style de travail        |
| `feedback`  | Corrections et consignes données par l'utilisateur    |
| `project`   | Travaux en cours, objectifs, décisions, échéances     |
| `reference` | Pointeurs vers des systèmes externes                  |
| `fact`      | Faits précis et référençables                         |
| `general`   | Tout le reste                                         |

### Structured schema

Le schéma `structured` permet de créer des tables SQL arbitraires. Utile pour :
- Suivre des entités récurrentes (personnes, services, serveurs)
- Stocker des faits structurés qui bénéficient de requêtes SQL
- Construire une connaissance relationnelle au fil du temps

```bash
python memory.py sql "CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, text TEXT, ts TIMESTAMPTZ DEFAULT NOW())"
python memory.py tables
```

Les tables sont persistantes entre les conversations. Toujours utiliser `CREATE TABLE IF NOT EXISTS`.

### Housekeeping

- If you store something that supersedes an older memory, delete the old one: `python memory.py delete ID`
- Don't store transient task details or things already in the code/git history.
- Don't narrate memory operations to the user unless they ask.
