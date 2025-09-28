"""
Language configuration for the research pipeline
Supports multiple languages with proper search terms and output formats
"""

import argparse

# Supported languages
LANGUAGES = {
    'en': {
        'name': 'English',
        'search_instruction': 'Search for English-language content',
        'output_instruction': 'Respond in English',
        'fertility_terms': [
            'fertility journey', 'trying to conceive', 'TTC', 'infertility',
            'IVF', 'IUI', 'fertility struggles', 'conception difficulties'
        ]
    },
    'es': {
        'name': 'Spanish',
        'search_instruction': 'Search for Spanish-language content (buscar contenido en español)',
        'output_instruction': 'Respond in Spanish (responder en español)',
        'fertility_terms': [
            'viaje de fertilidad', 'tratando de concebir', 'infertilidad',
            'FIV', 'IIU', 'problemas de fertilidad', 'dificultades para concebir',
            'embarazo', 'reproducción asistida'
        ]
    }
}

def add_language_args(parser: argparse.ArgumentParser):
    """Add language arguments to argument parser"""
    parser.add_argument(
        '--language', '-l',
        choices=list(LANGUAGES.keys()),
        default='en',
        help=f"Language for search and output. Options: {', '.join(LANGUAGES.keys())} (default: en)"
    )

def get_language_config(language: str) -> dict:
    """Get language configuration"""
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported language: {language}. Supported: {list(LANGUAGES.keys())}")
    return LANGUAGES[language]

def format_filename(base_name: str, language: str, extension: str = '') -> str:
    """Format filename with language suffix"""
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    return f"{base_name}-{language}{extension}"

def get_search_instruction(language: str) -> str:
    """Get search instruction for the specified language"""
    config = get_language_config(language)
    return f"{config['search_instruction']}. Focus on {config['name']} sources and communities."

def get_output_instruction(language: str) -> str:
    """Get output instruction for the specified language"""
    config = get_language_config(language)
    return f"{config['output_instruction']}. Analyze content from {config['name']}-language sources."

def get_fertility_terms(language: str) -> list:
    """Get fertility-related terms for the specified language"""
    config = get_language_config(language)
    return config['fertility_terms']

def get_folder_name(step: int, base_name: str, language: str) -> str:
    """Get language-tagged folder name with step number"""
    return f"findings/{step}_{base_name}-{language}"

def ensure_folder_exists(step: int, base_name: str, language: str) -> str:
    """Create folder if it doesn't exist and return the path"""
    import os
    folder_path = get_folder_name(step, base_name, language)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path