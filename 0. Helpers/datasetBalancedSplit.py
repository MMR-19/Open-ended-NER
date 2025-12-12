# imports
import pandas as pd
import numpy as np

from datasetProcessing import tokens_to_entities

# functions

def balanced_multilabel_sample(entity_dictionary, n_samples, random_state=73):
    np.random.seed(random_state)

    # Get all unique classes
    all_classes = sorted({cls for classes in entity_dictionary.values() for cls in classes})

    # Build DataFrame
    rows = []
    for sample_id, classes in entity_dictionary.items():
        row = {"id": sample_id}
        for cls in all_classes:
            row[cls] = int(cls in classes)
        rows.append(row)

    df = pd.DataFrame(rows)

    # Get label columns (all except 'id')
    label_cols = [c for c in df.columns if c != "id"]

    # Track selected indices and current label counts
    selected = []
    label_counts = np.zeros(len(label_cols), dtype=int)

    for _ in range(n_samples):
        # Compute how many labels are currently underrepresented
        target_mean = label_counts.mean() + 1e-6
        imbalance = target_mean - label_counts

        # Score each sample based on how well it helps balance the labels
        label_matrix = df[label_cols].values.astype(int)
        scores = label_matrix.dot(imbalance)

        # Pick the sample with the highest score (most helpful)
        idx = np.argmax(scores)
        selected.append(int(df.index[idx]))

        # Update label counts
        label_counts += label_matrix[idx]

        # Remove selected sample from future consideration
        df = df.drop(df.index[idx])

        if len(df) == 0:
            break

    return selected

def entity_map(dataset_split, entity_names_parsed, start_of_entity_indices, entity_index_to_name):
    total_instances = len(dataset_split)
    entity_map_dict = {}
    for idx, instance in enumerate(dataset_split):
        entity_list = tokens_to_entities(instance["tokens"], instance["ner_tags"], entity_names_parsed, start_of_entity_indices, entity_index_to_name)
        entity_map_dict[idx] = list(set([entity.entity for entity in entity_list]))
        print(idx+1, "/", total_instances, end="\r")
    return entity_map_dict