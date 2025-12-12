# Imports
from datasetProcessing import Entity

# Performance classes
class Performance:
    tp = 0 # true positives (true entities match llm entities)
    fp = 0 # false positives (llm entities that are not true entities)
    fn = 0 # false negatives (true entities that are not llm entities)

    def __init__(self, tp, fp, fn):
        self.tp = tp
        self.fp = fp
        self.fn = fn

    def precision(self):
        return 100 * self.tp / (self.tp + self.fp) if self.tp + self.fp > 0 else 0
    
    def recall(self):
        return 100 * self.tp / (self.tp + self.fn) if self.tp + self.fn > 0 else 0
    
    def f1(self):
        return 2 * (self.precision() * self.recall()) / (self.precision() + self.recall()) if self.precision() + self.recall() > 0 else 0

class Prediction:
    index: int = 0
    sentence: str = ""
    true_entities: list[Entity] = []
    llm_entities: list[dict] = []
    performance: Performance
    relaxed_performance: Performance

    def __init__(self, index, sentence):
        self.index = index
        self.sentence = sentence

    def set_results(self, true_entities, llm_entities):
        self.true_entities = true_entities
        self.llm_entities = llm_entities

    def compute_performance(self):
        tp = 0
        fp = 0
        fn = 0

        # # empty check
        # if (not self.true_entities or len(self.true_entities) == 0) and (not self.llm_entities or len(self.llm_entities) == 0):
        #     self.performance = Performance(1, 0, 0)
        #     return

        llm_entities_checked = [False] * len(self.llm_entities)
        
        for ground_truth in self.true_entities:
            for llm_index, llm_entity in enumerate(self.llm_entities):
                
                ground_truth_span = ground_truth.span.lower().strip()
                llm_entity_span = llm_entity['span'].lower().strip()
                ground_truth_entity = ground_truth.entity.lower().strip()
                llm_entity_entity = llm_entity['entity'].lower().strip()

                # check for exact matches (both span and entity type)
                span_match = ground_truth_span == llm_entity_span
                entity_match = ground_truth_entity == llm_entity_entity

                # true positive
                if span_match and entity_match:
                    tp += 1
                    llm_entities_checked[llm_index] = True
                    break
            
            # false negative
            else: # only if the loop never breaks
                fn += 1
        
        # false positives
        fp = len([checked for checked in llm_entities_checked if not checked])

        # update performance
        self.performance = Performance(tp, fp, fn)     
    
    def compute_relaxed_performance(self):
        tp = 0
        fp = 0
        fn = 0

        # # empty check
        # if (not self.true_entities or len(self.true_entities) == 0) and (not self.llm_entities or len(self.llm_entities) == 0):
        #     self.relaxed_performance = Performance(1, 0, 0)
        #     return
        
        llm_entities_checked = [False] * len(self.llm_entities)
        
        for ground_truth in self.true_entities:
            for llm_index, llm_entity in enumerate(self.llm_entities):
                
                ground_truth_span = ground_truth.span.lower().strip()
                llm_entity_span = llm_entity['span'].lower().strip()
                ground_truth_entity = ground_truth.entity.lower().strip()
                llm_entity_entity = llm_entity['entity'].lower().strip()

                # match check
                span_match = ground_truth_span == llm_entity_span
                entity_match = ground_truth_entity == llm_entity_entity

                if not span_match:

                    # check if spans are inside each other
                    if (llm_entity_span in ground_truth_span) or (ground_truth_span in llm_entity_span):
                        span_match = True

                if not entity_match:
                    
                    equivalence = {
                        # "person": ["politician", "scientist", "researcher", "writer", "musical artist"],
                        # "organisation": ["organization", "political party", "university", "conference", "political family", "location", "country"],
                        # "location": ["country"],
                        # "event": ["election"],
                        # "book": ["poem"],
                        # "protein": ["chemical compound"],
                        # "pessoa": ["personagem"],
                        # "organização": ["banda"],
                        # "localização": ["localidade", "local", "cidade", "país", "localizaçã", "localizaçãão"],
                        # "unidade orgânica": ["unidade", "organização", "universidade", "instituto", "instituição"],
                        # "data": ["ano", "mês", "dia"],
                        "organisation": ["organization", "orgnisation"],
                        "localização": ["localizaçã", "localizaçãão"],
                    }

                    # entities_always_ok = ["misc", "task"]

                    # # check if entities are always ok
                    # if ground_truth_entity in entities_always_ok or llm_entity_entity in entities_always_ok:
                    #     entity_match = True

                    # check for equivalences
                    for key, values in equivalence.items():
                        if (llm_entity_entity == key and ground_truth_entity in values) or (llm_entity_entity in values and ground_truth_entity == key):
                            entity_match = True
                            break

                if span_match and entity_match:
                    tp += 1
                    
                    # mark as checked
                    llm_entities_checked[llm_index] = True

                    break

            else: # not executed if the loop breaks
                fn += 1

        fp = len([checked for checked in llm_entities_checked if not checked])

        # update self
        self.relaxed_performance = Performance(tp, fp, fn)     
    
    def __str__(self):
        return f"Example #{self.index}, true: {len(self.true_entities)}, llm: {len(self.llm_entities)}\ntp: {self.performance.tp}, fp: {self.performance.fp}, fn: {self.performance.fn}\nprecision: {self.performance.precision()}, recall: {self.performance.recall()}, f1: {self.performance.f1()}"
