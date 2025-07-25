# Section Ranking Module
# Ranks extracted sections by importance and relevance

import numpy as np
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class SectionRanker:
    """
    Ranks document sections based on relevance, quality, and persona requirements.
    """
    
    def __init__(self):
        self.ranking_weights = {
            'relevance_score': 0.4,      # Persona/job relevance
            'quality_score': 0.25,       # Content quality
            'completeness_score': 0.15,  # Information completeness
            'position_score': 0.1,       # Document position
            'uniqueness_score': 0.1      # Content uniqueness
        }
    
    def rank_sections(self, sections: List[Dict[str, Any]], 
                     persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank sections by importance and relevance.
        
        Args:
            sections: List of extracted sections
            persona_profile: Persona matching profile
            
        Returns:
            Sorted list of sections with importance rankings
        """
        if not sections:
            return []
        
        # Calculate all scoring components
        for i, section in enumerate(sections):
            scores = self._calculate_all_scores(section, persona_profile, sections)
            section['scores'] = scores
            section['final_score'] = self._calculate_final_score(scores)
        
        # Sort by final score (descending)
        ranked_sections = sorted(sections, 
                               key=lambda x: x['final_score'], 
                               reverse=True)
        
        # Assign importance ranks
        for i, section in enumerate(ranked_sections):
            section['importance_rank'] = i + 1
        
        logger.info(f"Ranked {len(ranked_sections)} sections")
        return ranked_sections
    
    def _calculate_all_scores(self, section: Dict[str, Any], 
                            persona_profile: Dict[str, Any],
                            all_sections: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate all scoring components for a section."""
        
        return {
            'relevance_score': section.get('relevance_score', 0.0),
            'quality_score': self._calculate_quality_score(section),
            'completeness_score': self._calculate_completeness_score(section, persona_profile),
            'position_score': self._calculate_position_score(section),
            'uniqueness_score': self._calculate_uniqueness_score(section, all_sections)
        }
    
    def _calculate_final_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted final score."""
        final_score = 0.0
        
        for component, score in scores.items():
            weight = self.ranking_weights.get(component, 0.0)
            final_score += score * weight
        
        return final_score
    
    def _calculate_quality_score(self, section: Dict[str, Any]) -> float:
        """Calculate content quality score."""
        content = section.get('content', '')
        title = section.get('title', '')
        
        if not content:
            return 0.0
        
        # Component scores
        readability_score = self._assess_readability(content)
        structure_score = self._assess_structure(content)
        information_density = self._assess_information_density(content)
        title_quality = self._assess_title_quality(title)
        
        # Weighted combination
        quality_score = (
            readability_score * 0.3 +
            structure_score * 0.3 +
            information_density * 0.3 +
            title_quality * 0.1
        )
        
        return quality_score
    
    def _calculate_completeness_score(self, section: Dict[str, Any], 
                                    persona_profile: Dict[str, Any]) -> float:
        """Calculate information completeness score."""
        content = section.get('content', '')
        
        if not content:
            return 0.0
        
        # Check for different types of information
        has_specific_details = self._has_specific_details(content)
        has_actionable_info = self._has_actionable_information(content, persona_profile)
        has_examples = self._has_examples(content)
        has_quantitative_data = self._has_quantitative_data(content)
        
        # Calculate completeness
        completeness_factors = [
            has_specific_details,
            has_actionable_info,
            has_examples,
            has_quantitative_data
        ]
        
        return sum(completeness_factors) / len(completeness_factors)
    
    def _calculate_position_score(self, section: Dict[str, Any]) -> float:
        """Calculate score based on section position in document."""
        page_number = section.get('page_number', 1)
        
        # Early sections often contain key information
        if page_number == 1:
            return 1.0
        elif page_number <= 3:
            return 0.8
        elif page_number <= 5:
            return 0.6
        else:
            return 0.4
    
    def _calculate_uniqueness_score(self, section: Dict[str, Any], 
                                  all_sections: List[Dict[str, Any]]) -> float:
        """Calculate content uniqueness score."""
        current_content = section.get('content', '').lower()
        
        if not current_content:
            return 0.0
        
        # Compare with other sections
        similarity_scores = []
        
        for other_section in all_sections:
            if other_section is section:
                continue
            
            other_content = other_section.get('content', '').lower()
            if not other_content:
                continue
            
            similarity = self._calculate_text_similarity(current_content, other_content)
            similarity_scores.append(similarity)
        
        if not similarity_scores:
            return 1.0
        
        # Higher uniqueness = lower average similarity
        avg_similarity = np.mean(similarity_scores)
        return max(0.0, 1.0 - avg_similarity)
    
    def _assess_readability(self, content: str) -> float:
        """Assess text readability."""
        words = content.split()
        sentences = content.split('.')
        
        if not words or not sentences:
            return 0.0
        
        # Simple readability metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = np.mean([len(word) for word in words])
        
        # Optimal ranges for readability
        sentence_score = 1.0 if 10 <= avg_sentence_length <= 20 else 0.5
        word_score = 1.0 if 4 <= avg_word_length <= 6 else 0.5
        
        return (sentence_score + word_score) / 2
    
    def _assess_structure(self, content: str) -> float:
        """Assess content structure quality."""
        lines = content.split('\\n')
        
        # Check for structure indicators
        has_lists = any(':' in line or '•' in line or '-' in line[:5] for line in lines)
        has_paragraphs = len([line for line in lines if line.strip()]) > 1
        has_varied_length = len(set(len(line.split()) for line in lines if line.strip())) > 2
        
        structure_factors = [has_lists, has_paragraphs, has_varied_length]
        return sum(structure_factors) / len(structure_factors)
    
    def _assess_information_density(self, content: str) -> float:
        """Assess information density."""
        words = content.split()
        
        # Count informative words (nouns, verbs, adjectives)
        informative_words = [word for word in words 
                           if len(word) > 3 and word.isalpha()]
        
        if not words:
            return 0.0
        
        density = len(informative_words) / len(words)
        return min(density * 1.5, 1.0)  # Scale to 0-1 range
    
    def _assess_title_quality(self, title: str) -> float:
        """Assess title quality."""
        if not title:
            return 0.0
        
        # Title quality factors
        appropriate_length = 3 <= len(title.split()) <= 10
        has_meaningful_words = any(len(word) > 3 for word in title.split())
        not_generic = title.lower() not in ['untitled', 'section', 'chapter']
        
        quality_factors = [appropriate_length, has_meaningful_words, not_generic]
        return sum(quality_factors) / len(quality_factors)
    
    def _has_specific_details(self, content: str) -> bool:
        """Check if content has specific details."""
        # Look for specific indicators
        indicators = [
            r'\\b\\d+%',  # Percentages
            r'\\$\\d+',   # Money amounts
            r'\\b\\d{4}\\b',  # Years
            r'\\b\\d+\\s*(hours?|days?|weeks?|months?)\\b',  # Time periods
            r'\\b(specifically|particularly|exactly|precisely)\\b'  # Specificity words
        ]
        
        import re
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in indicators)
    
    def _has_actionable_information(self, content: str, persona_profile: Dict[str, Any]) -> bool:
        """Check if content has actionable information for the persona."""
        action_words = [
            'how to', 'steps', 'process', 'method', 'approach', 'strategy',
            'implement', 'create', 'develop', 'build', 'design', 'plan',
            'should', 'must', 'need to', 'important to', 'recommended'
        ]
        
        content_lower = content.lower()
        return any(word in content_lower for word in action_words)
    
    def _has_examples(self, content: str) -> bool:
        """Check if content contains examples."""
        example_indicators = [
            'for example', 'such as', 'including', 'like', 'instance',
            'e.g.', 'i.e.', 'namely', 'case study', 'illustration'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in example_indicators)
    
    def _has_quantitative_data(self, content: str) -> bool:
        """Check if content contains quantitative data."""
        import re
        
        # Look for numbers, statistics, measurements
        patterns = [
            r'\\b\\d+(\\.\\d+)?%',  # Percentages
            r'\\b\\d+(\\.\\d+)?\\s*(million|billion|thousand)',  # Large numbers
            r'\\b\\d+(\\.\\d+)?\\s*(kg|lb|oz|g|L|ml)',  # Measurements
            r'\\b\\d+(\\.\\d+)?\\s*degrees?',  # Temperatures
            r'\\b\\d+(\\.\\d+)?\\s*(minutes?|hours?|days?)'  # Time
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple word overlap similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
