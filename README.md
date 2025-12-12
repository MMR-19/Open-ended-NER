# Exploring LLM-based Approaches for Open-ended Named Entity Recognition in Low-resource Domains
Thesis to obtain the Master of Science Degree in Data Science and Engineering

---

### Disclaimer about data sources

We do not include any data source directly for copyright reasons.

### Folder "0. Helpers"

Helper python methods and scripts to support the main analysis.
- datasetBalancedSplit: Splitting datasets evenly
- datasetProcessing: Methods for parsing, for example, parsing entities from BIO format to JSON, etc...
- performance: functions to compute precision, recall and F1
- reflection_helpers: functions to support the error reflection analysis, including gettint a token context window

### Folder "2. Data Processing"

Notebooks and scripts to process the raw datasets into the format needed for the analysis. Includes _dataset_entities folder with full entities list for each dataset.

### Folder "3. Data Exploratory Analysis"

Notebooks to explore the datasets, and compute relevant summaries.
 
### Folder "4. Open-ended NER"

This is where the real magic happens. 
We follow a specific order since there are dependencies on our analysis. 

For example, to get in-context examples we first need to compute embeddings.

- Folders
  - _results: every individual LLM inference result
  - _performance: grouped F1 performance, by design variable
  - classification: individual training instance classification in entity/context/other. Also store the probabilities dictionary and total metrics for each dataset
  - embeddings: each instance embeddings (from Qwen3-Embedding-4B model)
  - entity_info: separate "description", "list" and "point entities" information for all entities
  - in_context: for each test instance, .txt files with in-context examples.
  - static: for each test instance, .txt files with static examples.

- Section 1 > Point Entities
  - 1.1: Gather central token examples for each entity
  - 1.2: Gather central span examples for each entity
  - 1.3: LLM inference loop for all "entity info" design variables

- Section 2 > In-context Learning
  - 2.1: Classify each training token into entity/context/other
  - 2.2: Compute each instance embeddings
  - 2.3 - 2.5: Gather in-context examples according to the criteria selected
  - 2.6: LLM inference loop for all "in-context" design variables

- Section 3 > Chain of Thought
  - 3.1: LLM inference loop for all "CoT" design variables

- Sections 4 > Evaluation
  - Evaluate performance (F1) of the experiments

- Section 5 > Error Reflection
  - 5: Error Analysis of previous experiments
  - For all three error reflection types (unseen, false negatives and boundary)
    - .1: Identity tokens for reflection
    - .2: LLM loop to reflect on the identified tokens
    - .3: Same LLM loop, but without CoT

- Sections 6 > Evaluation
  - 6.1: Evaluate performance (F1) of the Error Reflection experiments (custom evaluation needed)
  - 6.1.1: Same evaluation but focusing only on the instances with token reflections
  - 6.2: Evaluate Boundary reflection (different from other reflections, since entities are replaced instead of added)
