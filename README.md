# AI Secure Gateway

Prototype de vérification de prompts avec un petit LLM local.

## Installation

Dans le VENV du projet :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Installer Ollama, démarrer son service, puis télécharger le modèle :

```powershell
ollama pull llama3.2:3b
```

Variables optionnelles :

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:GUARDRAIL_MODEL = "llama3.2:3b"
```

## Utilisation

```powershell
python test.py
```

Le guardrail retourne une classification structurée. La fonction `decide_policy` transforme ensuite cette classification en `allow`, `block` ou `review`. Une erreur Ollama produit toujours `review`.

## Tests sans Ollama

```powershell
python -m unittest discover -s tests -v
```

## Mesurer la précision

Le dataset de démonstration est dans `data/prompt_safety.jsonl`. Chaque exemple possède une vérité terrain et un split.

```powershell
python evaluate_guardrail.py --split test
```

L'évaluation affiche accuracy, precision, recall, F1, taux de faux positifs, taux de faux négatifs et les erreurs. Pour un guardrail, surveiller en priorité le recall des prompts dangereux et examiner manuellement chaque faux négatif.

Le dataset fourni est uniquement un exemple de démarrage. Il doit être enrichi avec des cas réels, des formulations ambiguës et des négatifs difficiles avant toute utilisation en production.
