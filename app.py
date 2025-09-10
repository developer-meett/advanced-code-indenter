from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import subprocess
import tempfile
import os
import shutil
import logging
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.util import ClassNotFound

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logger.info("🚀 Advanced Code Indenter Server Starting...")
logger.info("📍 Access the application at: http://localhost:5001")
logger.info("🔧 API endpoints available:")
logger.info("   - Language Detection: /api/detect-language")
logger.info("   - Code Formatting: /api/indent")
logger.info("🎯 Supported Languages: Python, JavaScript, HTML, CSS, C++, Java, C#, Go, Ruby, PHP, TypeScript, JSON, XML")

# Language mapping for consistent naming
LANGUAGE_MAPPING = {
    'python': 'python',
    'python3': 'python',
    'javascript': 'javascript',
    'js': 'javascript',
    'html': 'html',
    'css': 'css',
    'c++': 'cpp',
    'cpp': 'cpp',
    'c': 'c',
    'java': 'java',
    'c#': 'csharp',
    'csharp': 'csharp',
    'go': 'go',
    'ruby': 'ruby',
    'php': 'php',
    'typescript': 'typescript',
    'json': 'json',
    'xml': 'xml'
}

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/detect-language', methods=['POST'])
def detect_language():
    """
    API endpoint to automatically detect the programming language of code
    
    Expected JSON payload:
    {
        "code": "code string to analyze"
    }
    
    Returns:
    {
        "language": "detected_language_name",
        "confidence": "high|medium|low"
    }
    or
    {
        "error": "error message"
    }
    """
    try:
        logger.info("Language detection request received")
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided in language detection request")
            return jsonify({"error": "No JSON data provided"}), 400
            
        code = data.get('code', '').strip()
        
        # Validate input
        if not code:
            logger.info("Empty code provided, returning text with low confidence")
            return jsonify({"language": "text", "confidence": "low"})
            
        if len(code) < 10:  # Too short to reliably detect
            logger.info("Code too short for reliable detection")
            return jsonify({"language": "text", "confidence": "low"})
            
        try:
            # Use pygments to guess the lexer/language
            lexer = guess_lexer(code)
            detected_name = lexer.name.lower()
            
            logger.debug(f"Pygments detected: {detected_name}")
            
            # First, try to use our enhanced pattern-based detection for better accuracy
            pattern_result = enhanced_pattern_detection(code)
            
            # If pattern detection is confident, use it
            if pattern_result['confidence'] in ['high', 'medium'] and pattern_result['language'] != 'text':
                logger.info(f"Pattern detection successful: {pattern_result['language']}")
                return jsonify({
                    "language": pattern_result['language'],
                    "confidence": pattern_result['confidence'],
                    "detected_by": "enhanced_patterns",
                    "pygments_detected": detected_name,
                    "pattern_scores": pattern_result.get('scores', {})
                })
            
            # Otherwise, try to map pygments result to our languages
            language = map_pygments_to_language(detected_name, code)
            confidence = get_confidence_for_language(language, code)
            
            return jsonify({
                "language": language,
                "confidence": confidence,
                "detected_by": "pygments_enhanced",
                "raw_detection": detected_name
            })
            
        except ClassNotFound:
            # Pygments couldn't identify the language, use our pattern detection
            logger.warning("Pygments failed to identify language, using pattern detection")
            return enhanced_pattern_detection_response(code)
        except Exception as e:
            logger.error(f"Pygments detection error: {e}")
            return enhanced_pattern_detection_response(code)
            
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500


def enhanced_pattern_detection(code):
    """Enhanced pattern-based language detection with better accuracy"""
    
    # Define comprehensive language patterns
    language_patterns = {
        'python': {
            'strong': ['def ', 'import ', 'from ', 'if __name__', 'print(', 'class ', 'elif ', 'lambda '],
            'medium': ['self.', 'True', 'False', 'None', 'range(', 'len(', 'str('],
            'weak': [':', 'and ', 'or ', 'not ', 'in ', 'is ']
        },
        'javascript': {
            'strong': ['function ', 'const ', 'let ', 'var ', '=>', 'console.log', 'document.', 'window.'],
            'medium': ['typeof ', 'null', 'undefined', '===', '!==', 'JSON.'],
            'weak': ['true', 'false', 'new ', 'this.']
        },
        'cpp': {
            'strong': ['#include', 'std::', 'cout', 'cin', 'using namespace', 'int main', '<<', '>>', 'endl'],
            'medium': ['class ', 'void ', 'int ', 'char ', 'float ', 'double ', 'return ', 'public:', 'private:'],
            'weak': ['{', '}', ';', '#define']
        },
        'java': {
            'strong': ['public class', 'public static', 'System.out', 'import java', 'public void', 'private '],
            'medium': ['String ', 'int ', 'boolean ', 'ArrayList', 'HashMap', 'throws '],
            'weak': ['public ', 'static ', 'final ', 'extends ', 'implements ']
        },
        'csharp': {
            'strong': ['using System', 'Console.', 'namespace ', 'public class', 'static void Main'],
            'medium': ['string ', 'int ', 'bool ', 'var ', 'List<', 'Dictionary<'],
            'weak': ['public ', 'private ', 'static ', 'class ']
        },
        'html': {
            'strong': ['<!DOCTYPE', '<html', '<head>', '<body>', '<div', '<script>', '<style>'],
            'medium': ['<p>', '<h1>', '<h2>', '<a href', '<img ', '<form>'],
            'weak': ['</', '>', 'class=', 'id=']
        },
        'css': {
            'strong': ['background:', 'color:', '@media', 'hover:', 'display:', 'position:', 'margin:', 'padding:'],
            'medium': ['font-', 'border:', 'width:', 'height:', 'text-', 'float:'],
            'weak': ['{', '}', ':', ';', 'px', '%']
        },
        'go': {
            'strong': ['package ', 'func ', 'import ', 'fmt.', 'go ', 'defer '],
            'medium': ['var ', 'type ', 'struct ', 'interface ', 'chan '],
            'weak': [':=', 'range ', 'make(', 'len(']
        },
        'ruby': {
            'strong': ['def ', 'end', 'puts ', 'require ', 'class ', 'module '],
            'medium': ['@', '@@', 'nil', 'true', 'false', 'unless '],
            'weak': ['do |', '|', 'each ', 'map ']
        },
        'php': {
            'strong': ['<?php', '<?=', '$_GET', '$_POST', 'function ', 'echo ', 'print '],
            'medium': ['$', '->', '::', 'array(', 'isset('],
            'weak': [';', '==', '!=', '&&', '||']
        },
        'typescript': {
            'strong': ['interface ', 'type ', ': string', ': number', ': boolean', 'export ', 'import '],
            'medium': ['async ', 'await ', 'Promise<', 'Array<', 'readonly '],
            'weak': ['const ', 'let ', 'var ', '=>']
        },
        'json': {
            'strong': ['":', '",', '"}', '"]', '": {', '": ['],
            'medium': ['true', 'false', 'null'],
            'weak': ['{', '}', '[', ']', '"']
        },
        'xml': {
            'strong': ['<?xml', '<!DOCTYPE', '</', 'xmlns:', 'encoding='],
            'medium': ['<root>', '</root>', 'version=', 'standalone='],
            'weak': ['<', '>', '=', '"']
        }
    }
    
    # Calculate scores for each language
    scores = {}
    for lang, patterns in language_patterns.items():
        score = 0
        # Strong patterns get 3 points
        score += sum(3 for pattern in patterns['strong'] if pattern in code)
        # Medium patterns get 2 points
        score += sum(2 for pattern in patterns['medium'] if pattern in code)
        # Weak patterns get 1 point, but only count first few matches
        weak_matches = sum(1 for pattern in patterns['weak'] if pattern in code)
        score += min(weak_matches, 3)  # Cap weak pattern contribution
        
        scores[lang] = score
    
    # Find the language with the highest score
    max_score = max(scores.values()) if scores.values() else 0
    detected_language = "text"
    confidence = "low"
    
    if max_score > 0:
        detected_language = max(scores, key=scores.get)
        
        # Determine confidence based on score
        if max_score >= 6:
            confidence = "high"
        elif max_score >= 3:
            confidence = "medium"
        else:
            confidence = "low"
    
    return {
        "language": detected_language,
        "confidence": confidence,
        "scores": scores,
        "max_score": max_score
    }

def enhanced_pattern_detection_response(code):
    """Return enhanced pattern detection as JSON response"""
    result = enhanced_pattern_detection(code)
    return jsonify({
        "language": result["language"],
        "confidence": result["confidence"],
        "detected_by": "enhanced_patterns_fallback",
        "pattern_scores": result["scores"]
    })

def map_pygments_to_language(detected_name, code):
    """Map pygments detected name to our language names"""
    detected_lower = detected_name.lower()
    
    # Direct mappings
    if 'python' in detected_lower:
        return 'python'
    elif any(term in detected_lower for term in ['javascript', 'ecmascript', 'js']):
        return 'javascript'
    elif 'html' in detected_lower:
        return 'html'
    elif 'css' in detected_lower:
        # Double-check CSS vs C++ confusion
        if any(pattern in code for pattern in ['#include', 'std::', 'cout', 'int main']):
            return 'cpp'
        return 'css'
    elif any(term in detected_lower for term in ['c++', 'cpp']):
        return 'cpp'
    elif 'c' in detected_lower and any(pattern in code for pattern in ['#include', 'stdio.h', 'printf']):
        return 'cpp'  # Treat C as C++ for formatting purposes
    elif 'java' in detected_lower:
        return 'java'
    elif any(term in detected_lower for term in ['c#', 'csharp']):
        return 'csharp'
    elif 'go' in detected_lower:
        return 'go'
    elif 'ruby' in detected_lower:
        return 'ruby'
    elif 'php' in detected_lower:
        return 'php'
    elif 'typescript' in detected_lower:
        return 'typescript'
    elif 'json' in detected_lower:
        return 'json'
    elif 'xml' in detected_lower:
        return 'xml'
    else:
        return 'text'

def get_confidence_for_language(language, code):
    """Get confidence level for detected language based on code content"""
    confidence_patterns = {
        'python': ['def ', 'import ', 'print(', 'if __name__'],
        'javascript': ['function', 'const ', 'let ', '=>', 'console.log'],
        'cpp': ['#include', 'std::', 'cout', 'using namespace'],
        'java': ['public class', 'System.out', 'public static'],
        'csharp': ['using System', 'Console.', 'namespace '],
        'html': ['<!DOCTYPE', '<html', '<head>', '<body>'],
        'css': ['background:', 'color:', '@media', 'hover:'],
        'go': ['package ', 'func ', 'fmt.'],
        'ruby': ['def ', 'end', 'puts '],
        'php': ['<?php', '$', 'echo '],
        'typescript': ['interface ', 'type ', ': string'],
        'json': ['":', '",', 'true', 'false', 'null'],
        'xml': ['<?xml', '<!DOCTYPE', 'xmlns:']
    }
    
    if language in confidence_patterns:
        matches = sum(1 for pattern in confidence_patterns[language] if pattern in code)
        if matches >= 3:
            return 'high'
        elif matches >= 1:
            return 'medium'
    
    return 'low'


def fallback_language_detection(code):
    """Fallback language detection using enhanced pattern matching"""
    result = enhanced_pattern_detection(code)
    return jsonify({
        "language": result["language"],
        "confidence": result["confidence"],
        "detected_by": "enhanced_fallback",
        "pattern_scores": result["scores"]
    })


@app.route('/api/indent', methods=['POST'])
def indent_code():
    """
    Enhanced API endpoint to format code for multiple programming languages
    
    Expected JSON payload:
    {
        "code": "unformatted code string",
        "language": "python|javascript|html|css|cpp|java|csharp|go|ruby|php|typescript|json|xml"
    }
    
    Returns:
    {
        "indented_code": "formatted code string"
    }
    or
    {
        "error": "error message"
    }
    """
    try:
        logger.info("Code formatting request received")
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided in formatting request")
            return jsonify({"error": "No JSON data provided"}), 400
            
        code = data.get('code', '').strip()
        language = data.get('language', '').lower()
        
        # Validate input
        if not code:
            logger.warning("No code provided in formatting request")
            return jsonify({"error": "No code provided"}), 400
            
        if not language:
            logger.warning("No language specified in formatting request")
            return jsonify({"error": "No language specified"}), 400
            
        # Normalize language name
        language = LANGUAGE_MAPPING.get(language, language)
        logger.info(f"Formatting {language} code ({len(code)} characters)")
        
        # Format code based on language
        if language == 'python':
            try:
                formatted_code = format_python_with_black(code)
                logger.info("Python code formatted successfully")
            except Exception as e:
                logger.error(f"Python formatting error: {str(e)}")
                formatted_code = code  # Return original on failure
                
        elif language in ['javascript', 'js']:
            try:
                formatted_code = format_javascript_with_prettier(code)
                logger.info("JavaScript code formatted successfully")
            except Exception as e:
                logger.error(f"JavaScript formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'typescript':
            try:
                formatted_code = format_typescript_with_prettier(code)
                logger.info("TypeScript code formatted successfully")
            except Exception as e:
                logger.error(f"TypeScript formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'html':
            try:
                formatted_code = format_html_with_prettier(code)
                logger.info("HTML code formatted successfully")
            except Exception as e:
                logger.error(f"HTML formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'css':
            try:
                formatted_code = format_css_with_prettier(code)
                logger.info("CSS code formatted successfully")
            except Exception as e:
                logger.error(f"CSS formatting error: {str(e)}")
                formatted_code = code
                
        elif language in ['cpp', 'c', 'java', 'csharp']:
            try:
                formatted_code = format_with_clang_format(code, language)
                logger.info(f"{language.upper()} code formatted successfully")
            except Exception as e:
                logger.error(f"C/C++/Java/C# formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'go':
            try:
                formatted_code = format_with_gofmt(code)
                logger.info("Go code formatted successfully")
            except Exception as e:
                logger.error(f"Go formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'ruby':
            try:
                formatted_code = format_ruby_with_prettier(code)
                logger.info("Ruby code formatted successfully")
            except Exception as e:
                logger.error(f"Ruby formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'php':
            try:
                formatted_code = format_php_with_cs_fixer(code)
                logger.info("PHP code formatted successfully")
            except Exception as e:
                logger.error(f"PHP formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'json':
            try:
                # Parse and reformat JSON
                parsed = json.loads(code)
                formatted_code = json.dumps(parsed, indent=2, sort_keys=True)
                logger.info("JSON formatted successfully")
            except Exception as e:
                logger.error(f"JSON formatting error: {str(e)}")
                formatted_code = code
                
        elif language == 'xml':
            try:
                formatted_code = format_xml_with_prettier(code)
                logger.info("XML code formatted successfully")
            except Exception as e:
                logger.error(f"XML formatting error: {str(e)}")
                formatted_code = code
                
        else:
            logger.warning(f"Unsupported language requested: {language}")
            return jsonify({"error": f"Language '{language}' is not supported for formatting. Supported languages: python, javascript, html, css, cpp, java, csharp, go, ruby, php, typescript, json, xml"}), 400
            
        logger.info("Code formatting completed successfully")
        return jsonify({"indented_code": formatted_code})
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in request: {e}")
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        logger.error(f"Unexpected error in code formatting: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

def format_python_with_black(code):
    """
    Format Python code using a robust two-stage process.
    This version will raise an error if dependencies are not found.
    """
    # Stage 1: Check for and use autopep8
    try:
        import autopep8
        autopep8_fixed_code = autopep8.fix_code(code, options={'aggressive': 2})
    except ImportError:
        logger.error("CRITICAL: autopep8 is not installed in the environment.")
        # Raise an exception to make the failure visible
        raise RuntimeError("Formatting failed: autopep8 is missing from the server environment.")
    except Exception as e:
        logger.error(f"autopep8 encountered an error: {e}")
        return code

    if not autopep8_fixed_code.strip():
        autopep8_fixed_code = code

    # Stage 2: Check for and use black
    try:
        import black
        mode = black.Mode(line_length=88)
        black_formatted_code = black.format_str(autopep8_fixed_code, mode=mode)

        if not black_formatted_code.strip():
            logger.warning("Black returned an empty string, reverting to autopep8 result.")
            return autopep8_fixed_code

        return black_formatted_code

    except ImportError:
        logger.error("CRITICAL: black is not installed in the environment.")
        # Raise an exception to make the failure visible
        raise RuntimeError("Formatting failed: black is missing from the server environment.")
    except Exception as e:
        logger.warning(f"Black formatting failed with an exception: {e}. Reverting to autopep8 result.")
        return autopep8_fixed_code

def format_javascript_with_prettier(code):
    """Format JavaScript using Prettier CLI"""
    try:
        # Check if npx and prettier are available
        result = subprocess.run([
            'npx', 'prettier', '--parser', 'babel', '--stdin-filepath', 'temp.js'
        ], input=code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Prettier failed: {result.stderr}")
            
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Prettier not available for JavaScript: {e}")
        return format_js_fallback(code)
    except Exception as e:
        logger.error(f"JavaScript prettier error: {e}")
        return format_js_fallback(code)

def format_typescript_with_prettier(code):
    """Format TypeScript using Prettier CLI"""
    try:
        result = subprocess.run([
            'npx', 'prettier', '--parser', 'typescript', '--stdin-filepath', 'temp.ts'
        ], input=code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Prettier failed: {result.stderr}")
            
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Prettier not available for TypeScript: {e}")
        return format_js_fallback(code)
    except Exception as e:
        logger.error(f"TypeScript prettier error: {e}")
        return format_js_fallback(code)

def format_html_with_prettier(code):
    """Format HTML using Prettier CLI"""
    try:
        result = subprocess.run([
            'npx', 'prettier', '--parser', 'html', '--stdin-filepath', 'temp.html'
        ], input=code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Prettier failed: {result.stderr}")
            
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"Prettier not available for HTML: {e}")
        return format_html_fallback(code)
    except Exception as e:
        print(f"HTML prettier error: {e}")
        return format_html_fallback(code)

def format_css_with_prettier(code):
    """Format CSS using Prettier CLI"""
    try:
        result = subprocess.run([
            'npx', 'prettier', '--parser', 'css', '--stdin-filepath', 'temp.css'
        ], input=code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Prettier failed: {result.stderr}")
            
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"Prettier not available for CSS: {e}")
        return format_css_fallback(code)
    except Exception as e:
        print(f"CSS prettier error: {e}")
        return format_css_fallback(code)

def format_with_clang_format(code, language):
    """Format C/C++/Java/C# code using clang-format"""
    # Map language to file extension and clang-format style
    extension_map = {
        'cpp': 'cpp',
        'c': 'c', 
        'java': 'java',
        'csharp': 'cs'
    }
    
    style_map = {
        'cpp': 'Google',
        'c': 'Google',
        'java': 'Google',
        'csharp': 'Microsoft'
    }
    
    extension = extension_map.get(language, 'cpp')
    style = style_map.get(language, 'Google')
    
    try:
        # Create temporary file with proper extension
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{extension}', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        # Run clang-format
        result = subprocess.run([
            'clang-format',
            f'--style={style}',
            '--assume-filename', f'temp.{extension}',
            temp_file_path
        ], capture_output=True, text=True, timeout=30)
        
        # Clean up
        os.unlink(temp_file_path)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"clang-format failed: {result.stderr}")
            
    except FileNotFoundError:
        print(f"clang-format not found for {language}")
        return code
    except subprocess.TimeoutExpired:
        print(f"clang-format timed out for {language}")
        return code
    except Exception as e:
        print(f"clang-format error for {language}: {e}")
        return code

def format_with_gofmt(code):
    """Format Go code using gofmt"""
    try:
        result = subprocess.run([
            'gofmt'
        ], input=code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"gofmt failed: {result.stderr}")
            
    except FileNotFoundError:
        print("gofmt not found. Please install Go to format Go code.")
        return code
    except subprocess.TimeoutExpired:
        print("gofmt timed out")
        return code
    except Exception as e:
        print(f"gofmt error: {e}")
        return code

def format_ruby_with_prettier(code):
    """Format Ruby using Prettier CLI (with ruby plugin)"""
    try:
        result = subprocess.run([
            'npx', 'prettier', '--parser', 'ruby', '--stdin-filepath', 'temp.rb'
        ], input=code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Prettier failed: {result.stderr}")
            
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"Prettier not available for Ruby: {e}")
        return format_ruby_fallback(code)
    except Exception as e:
        print(f"Ruby prettier error: {e}")
        return format_ruby_fallback(code)

def format_php_with_cs_fixer(code):
    """Format PHP using php-cs-fixer or phpcbf"""
    try:
        # Try php-cs-fixer first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        # Try php-cs-fixer
        result = subprocess.run([
            'php-cs-fixer', 'fix', temp_file_path, '--quiet'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            with open(temp_file_path, 'r') as f:
                formatted = f.read()
            os.unlink(temp_file_path)
            return formatted
        else:
            # Try phpcbf as alternative
            result = subprocess.run([
                'phpcbf', '--standard=PSR12', temp_file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode in [0, 1]:  # phpcbf returns 1 when it fixes files
                with open(temp_file_path, 'r') as f:
                    formatted = f.read()
                os.unlink(temp_file_path)
                return formatted
            else:
                os.unlink(temp_file_path)
                raise Exception("Both php-cs-fixer and phpcbf failed")
            
    except FileNotFoundError:
        print("PHP formatters not found")
        return code
    except subprocess.TimeoutExpired:
        print("PHP formatter timed out")
        return code
    except Exception as e:
        print(f"PHP formatting error: {e}")
        return code

def format_xml_with_prettier(code):
    """Format XML using Prettier CLI"""
    try:
        result = subprocess.run([
            'npx', 'prettier', '--parser', 'xml', '--stdin-filepath', 'temp.xml'
        ], input=code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Prettier failed: {result.stderr}")
            
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"Prettier not available for XML: {e}")
        return format_xml_fallback(code)
    except Exception as e:
        print(f"XML prettier error: {e}")
        return format_xml_fallback(code)

# Fallback formatters for when main tools are not available
def format_js_fallback(code):
    """Basic JavaScript fallback formatting"""
    try:
        import jsbeautifier
        options = jsbeautifier.default_options()
        options.indent_size = 2
        options.space_in_empty_paren = False
        options.keep_array_indentation = True
        return jsbeautifier.beautify(code, options)
    except ImportError:
        return code

def format_html_fallback(code):
    """Basic HTML fallback formatting"""
    try:
        import jsbeautifier
        options = jsbeautifier.default_options()
        options.indent_size = 2
        options.wrap_line_length = 80
        options.preserve_newlines = True
        return jsbeautifier.beautify_html(code, options)
    except ImportError:
        return code

def format_css_fallback(code):
    """Basic CSS fallback formatting"""
    try:
        import jsbeautifier
        options = jsbeautifier.default_options()
        options.indent_size = 2
        options.newline_between_rules = True
        return jsbeautifier.beautify_css(code, options)
    except ImportError:
        return code

def format_ruby_fallback(code):
    """Basic Ruby fallback formatting"""
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue
            
        # Decrease indent for end, }, ]
        if any(stripped.startswith(keyword) for keyword in ['end', '}', ']', 'elsif', 'else', 'rescue', 'ensure']):
            if not stripped.startswith('else'):
                indent_level = max(0, indent_level - 1)
            
        # Add line with proper indentation
        formatted_lines.append('  ' * indent_level + stripped)
        
        # Increase indent for def, class, if, while, etc.
        if any(stripped.startswith(keyword) for keyword in ['def ', 'class ', 'module ', 'if ', 'unless ', 'while ', 'for ', 'begin', 'case ', 'elsif ', 'else']):
            indent_level += 1
        elif stripped.endswith(' do') or stripped.endswith('{') or stripped.endswith('['):
            indent_level += 1
            
    return '\n'.join(formatted_lines)

def format_xml_fallback(code):
    """Basic XML fallback formatting"""
    try:
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(code)
        pretty = dom.toprettyxml(indent="  ")
        # Remove extra blank lines
        lines = [line for line in pretty.splitlines() if line.strip()]
        return '\n'.join(lines)
    except:
        # Basic indentation fallback
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            if stripped.startswith('</'):
                indent_level = max(0, indent_level - 1)
                
            formatted_lines.append('  ' * indent_level + stripped)
            
            if stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>') and not stripped.startswith('<?'):
                # Check if it's a self-closing tag or has closing tag on same line
                if '>' in stripped and stripped.count('<') == stripped.count('</') + 1:
                    pass  # Self-contained tag
                else:
                    indent_level += 1
                
        return '\n'.join(formatted_lines)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("🚀 Advanced Code Indenter Server Starting...")
    logger.info("📍 Access the application at: http://localhost:5001")
    logger.info("🔧 API endpoints available:")
    logger.info("   - Language Detection: /api/detect-language")
    logger.info("   - Code Formatting: /api/indent")
    logger.info("🎯 Supported Languages: Python, JavaScript, HTML, CSS, C++, Java, C#, Go, Ruby, PHP, TypeScript, JSON, XML")
    app.run(host='0.0.0.0', port=5001)
