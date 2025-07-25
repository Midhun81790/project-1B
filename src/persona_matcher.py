# Persona Matching Module
# Analyzes persona requirements and calculates content relevance

import re
import numpy as np
from typing import Dict, List, Any, Set
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class PersonaMatcher:
    """
    Handles persona analysis and content relevance scoring.
    """
    
    def __init__(self):
        # Persona-specific keywords and weights
        self.persona_keywords = {
            'academic': {
                'researcher': ['research', 'study', 'analysis', 'methodology', 'findings', 
                             'literature', 'experiment', 'hypothesis', 'theory', 'data'],
                'phd_student': ['dissertation', 'thesis', 'literature_review', 'research', 
                              'analysis', 'methodology', 'academic', 'study'],
                'professor': ['teaching', 'curriculum', 'academic', 'research', 'publication',
                            'peer_review', 'methodology', 'theory'],
            },
            'business': {
                'analyst': ['analysis', 'market', 'trends', 'data', 'financial', 'performance',
                          'competitive', 'forecast', 'investment', 'revenue'],
                'manager': ['strategy', 'management', 'leadership', 'team', 'performance',
                          'planning', 'execution', 'budget', 'resources'],
                'consultant': ['advisory', 'strategy', 'solution', 'recommendation', 'analysis',
                             'optimization', 'process', 'improvement'],
            },
            'technical': {
                'developer': ['development', 'coding', 'programming', 'implementation', 
                            'software', 'system', 'architecture', 'framework'],
                'architect': ['architecture', 'design', 'system', 'scalability', 'integration',
                            'infrastructure', 'solution', 'technical'],
                'engineer': ['engineering', 'technical', 'implementation', 'solution',
                           'optimization', 'performance', 'system'],
            },
            'food': {
                'contractor': ['menu', 'catering', 'service', 'preparation', 'cooking',
                             'ingredients', 'dietary', 'nutrition', 'buffet'],
                'chef': ['cooking', 'recipe', 'cuisine', 'preparation', 'ingredients',
                        'technique', 'flavor', 'presentation'],
                'nutritionist': ['nutrition', 'dietary', 'health', 'vitamins', 'minerals',
                               'balanced', 'wellness', 'food_safety'],
            },
            'travel': {
                'planner': ['itinerary', 'destination', 'accommodation', 'transportation',
                          'activities', 'budget', 'booking', 'schedule'],
                'guide': ['local', 'culture', 'attractions', 'recommendations', 'experience',
                        'sightseeing', 'history', 'customs'],
                'agent': ['booking', 'reservation', 'package', 'deal', 'travel_insurance',
                        'documentation', 'visa', 'passport'],
            },
            'hr': {
                'professional': ['onboarding', 'compliance', 'forms', 'documentation', 
                               'employee', 'hiring', 'training', 'policies'],
                'manager': ['team', 'performance', 'development', 'recruitment', 'retention',
                          'culture', 'engagement', 'leadership'],
                'specialist': ['specialized', 'expert', 'certification', 'compliance',
                             'regulations', 'standards', 'procedures'],
            }
        }
        
        # Job-specific keywords
        self.job_keywords = {
            'analysis': ['analyze', 'examine', 'investigate', 'study', 'review', 'assess'],
            'planning': ['plan', 'organize', 'schedule', 'prepare', 'design', 'create'],
            'management': ['manage', 'coordinate', 'oversee', 'supervise', 'direct', 'lead'],
            'creation': ['create', 'develop', 'build', 'generate', 'produce', 'make'],
            'review': ['review', 'evaluate', 'assess', 'critique', 'examine', 'inspect'],
            'comparison': ['compare', 'contrast', 'versus', 'difference', 'similarity'],
            'recommendation': ['recommend', 'suggest', 'propose', 'advise', 'counsel'],
        }
    
    def analyze_persona(self, persona: Dict[str, Any], 
                       job_to_be_done: Any) -> Dict[str, Any]:
        """
        Analyze persona and job requirements to create a matching profile.
        
        Args:
            persona: Persona information with role (dict or string)
            job_to_be_done: Job description and requirements (dict or string)
            
        Returns:
            Comprehensive persona profile for matching
        """
        # Handle different input formats for persona
        if isinstance(persona, dict):
            role = persona.get('role', '').lower()
            focus = persona.get('focus', '')
        else:
            role = str(persona).lower()
            focus = ''
        
        # Handle different input formats for job_to_be_done
        if isinstance(job_to_be_done, dict):
            task = job_to_be_done.get('task', '').lower()
        else:
            task = str(job_to_be_done).lower()
        
        # Enhance role with focus if available
        full_role = f"{role} {focus}".strip() if focus else role
        
        # Determine domain and specific role
        domain, specific_role = self._classify_persona(full_role)
        
        # Extract job requirements
        job_type = self._classify_job(task)
        
        # Get relevant keywords
        persona_keywords = self._get_persona_keywords(domain, specific_role)
        job_keywords = self._get_job_keywords(job_type)
        task_keywords = self._extract_task_keywords(task)
        
        # Combine all keywords with weights
        keyword_weights = {}
        
        # Persona keywords (high weight)
        for keyword in persona_keywords:
            keyword_weights[keyword] = 3.0
        
        # Job type keywords (medium weight)
        for keyword in job_keywords:
            keyword_weights[keyword] = 2.0
        
        # Task-specific keywords (high weight)
        for keyword in task_keywords:
            keyword_weights[keyword] = 2.5
        
        profile = {
            'domain': domain,
            'role': specific_role,
            'job_type': job_type,
            'task_description': task,
            'keyword_weights': keyword_weights,
            'all_keywords': set(keyword_weights.keys()),
            'priority_keywords': self._get_priority_keywords(task)
        }
        
        logger.info(f"Created persona profile: {domain}/{specific_role} for {job_type}")
        logger.debug(f"Keywords: {len(keyword_weights)} total")
        
        return profile
    
    def calculate_relevance(self, section: Dict[str, Any], 
                          persona_profile: Dict[str, Any]) -> float:
        """
        Calculate relevance score for a section based on persona profile.
        
        Args:
            section: Text section with content
            persona_profile: Persona matching profile
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        content = section.get('content', '').lower()
        title = section.get('title', '').lower()
        
        if not content:
            return 0.0
        
        # Calculate different relevance components
        keyword_score = self._calculate_keyword_score(content, persona_profile)
        title_score = self._calculate_title_score(title, persona_profile)
        context_score = self._calculate_context_score(content, persona_profile)
        length_score = self._calculate_length_score(content)
        
        # Weighted combination
        total_score = (
            keyword_score * 0.4 +
            title_score * 0.3 +
            context_score * 0.2 +
            length_score * 0.1
        )
        
        return min(total_score, 1.0)
    
    def _classify_persona(self, role: str) -> tuple:
        """Classify persona into domain and specific role."""
        role = role.lower()
        
        # Check for domain indicators
        if any(word in role for word in ['research', 'academic', 'phd', 'professor', 'student']):
            domain = 'academic'
            if 'phd' in role or 'student' in role:
                specific_role = 'phd_student'
            elif 'professor' in role:
                specific_role = 'professor'
            else:
                specific_role = 'researcher'
        
        elif any(word in role for word in ['analyst', 'business', 'investment', 'financial']):
            domain = 'business'
            if 'analyst' in role:
                specific_role = 'analyst'
            elif 'manager' in role:
                specific_role = 'manager'
            else:
                specific_role = 'consultant'
        
        elif any(word in role for word in ['developer', 'engineer', 'technical', 'architect']):
            domain = 'technical'
            if 'developer' in role:
                specific_role = 'developer'
            elif 'architect' in role:
                specific_role = 'architect'
            else:
                specific_role = 'engineer'
        
        elif any(word in role for word in ['food', 'chef', 'contractor', 'cook', 'catering']):
            domain = 'food'
            if 'chef' in role:
                specific_role = 'chef'
            elif 'nutrition' in role:
                specific_role = 'nutritionist'
            else:
                specific_role = 'contractor'
        
        elif any(word in role for word in ['travel', 'planner', 'guide', 'agent']):
            domain = 'travel'
            if 'planner' in role:
                specific_role = 'planner'
            elif 'guide' in role:
                specific_role = 'guide'
            else:
                specific_role = 'agent'
        
        elif any(word in role for word in ['hr', 'human', 'professional']):
            domain = 'hr'
            if 'manager' in role:
                specific_role = 'manager'
            elif 'specialist' in role:
                specific_role = 'specialist'
            else:
                specific_role = 'professional'
        
        else:
            domain = 'general'
            specific_role = 'professional'
        
        return domain, specific_role
    
    def _classify_job(self, task: str) -> str:
        """Classify job type from task description."""
        task = task.lower()
        
        if any(word in task for word in ['analyze', 'analysis', 'examine', 'study']):
            return 'analysis'
        elif any(word in task for word in ['plan', 'planning', 'organize', 'schedule']):
            return 'planning'
        elif any(word in task for word in ['manage', 'management', 'coordinate']):
            return 'management'
        elif any(word in task for word in ['create', 'develop', 'build', 'generate']):
            return 'creation'
        elif any(word in task for word in ['review', 'evaluate', 'assess']):
            return 'review'
        elif any(word in task for word in ['compare', 'comparison', 'versus']):
            return 'comparison'
        elif any(word in task for word in ['recommend', 'suggest', 'advice']):
            return 'recommendation'
        else:
            return 'general'
    
    def _get_persona_keywords(self, domain: str, specific_role: str) -> List[str]:
        """Get keywords for specific persona."""
        if domain in self.persona_keywords and specific_role in self.persona_keywords[domain]:
            return self.persona_keywords[domain][specific_role]
        return []
    
    def _get_job_keywords(self, job_type: str) -> List[str]:
        """Get keywords for job type."""
        return self.job_keywords.get(job_type, [])
    
    def _extract_task_keywords(self, task: str) -> List[str]:
        """Extract important keywords from task description."""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\\b\\w{4,}\\b', task.lower())
        
        # Remove common stop words
        stop_words = {'this', 'that', 'with', 'from', 'they', 'been', 'have', 
                     'will', 'would', 'could', 'should', 'there', 'their'}
        
        keywords = [word for word in words if word not in stop_words]
        
        # Return most frequent keywords (up to 10)
        counter = Counter(keywords)
        return [word for word, count in counter.most_common(10)]
    
    def _get_priority_keywords(self, task: str) -> Set[str]:
        """Get high-priority keywords from task."""
        # Extract specific terms that are likely important
        priority_terms = set()
        
        # Look for quoted terms or specific requirements
        quoted = re.findall(r'"([^"]*)"', task)
        priority_terms.update([term.lower() for term in quoted])
        
        # Look for numbers and specific quantities
        numbers = re.findall(r'\\b\\d+\\b', task)
        priority_terms.update(numbers)
        
        # Look for specific domain terms
        if 'vegetarian' in task.lower():
            priority_terms.add('vegetarian')
        if 'gluten-free' in task.lower():
            priority_terms.add('gluten-free')
        if 'buffet' in task.lower():
            priority_terms.add('buffet')
        
        return priority_terms
    
    def _calculate_keyword_score(self, content: str, persona_profile: Dict[str, Any]) -> float:
        """Calculate keyword-based relevance score."""
        keyword_weights = persona_profile['keyword_weights']
        words = content.lower().split()
        
        total_score = 0.0
        total_weight = sum(keyword_weights.values())
        
        if total_weight == 0:
            return 0.0
        
        for word in words:
            if word in keyword_weights:
                total_score += keyword_weights[word]
        
        # Normalize by content length and keyword weights
        content_factor = min(len(words) / 100, 1.0)  # Longer content gets slight bonus
        normalized_score = (total_score / total_weight) * content_factor
        
        return min(normalized_score, 1.0)
    
    def _calculate_title_score(self, title: str, persona_profile: Dict[str, Any]) -> float:
        """Calculate title-based relevance score."""
        if not title:
            return 0.0
        
        keyword_weights = persona_profile['keyword_weights']
        title_words = title.lower().split()
        
        score = 0.0
        for word in title_words:
            if word in keyword_weights:
                score += keyword_weights[word] * 2  # Title keywords weighted higher
        
        # Normalize by title length
        if len(title_words) > 0:
            score = score / len(title_words)
        
        return min(score / 5.0, 1.0)  # Scale down to 0-1 range
    
    def _calculate_context_score(self, content: str, persona_profile: Dict[str, Any]) -> float:
        """Calculate contextual relevance score."""
        priority_keywords = persona_profile['priority_keywords']
        
        if not priority_keywords:
            return 0.5  # Neutral score if no priority keywords
        
        content_lower = content.lower()
        matches = sum(1 for keyword in priority_keywords if keyword in content_lower)
        
        return min(matches / len(priority_keywords), 1.0)
    
    def _calculate_length_score(self, content: str) -> float:
        """Calculate score based on content length (prefer moderate length)."""
        word_count = len(content.split())
        
        # Optimal range: 50-300 words
        if 50 <= word_count <= 300:
            return 1.0
        elif word_count < 50:
            return word_count / 50.0
        else:
            # Diminishing returns for very long content
            return max(0.5, 300.0 / word_count)
