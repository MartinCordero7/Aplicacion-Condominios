import os
import re

import sys

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content

    # Add import if not exists
    import_stmt = "import '../../../core/network/api_error_handler.dart';"
    if import_stmt not in content:
        # Insert after the last import
        imports = re.findall(r"^import '.*?';$", content, re.MULTILINE)
        if imports:
            last_import = imports[-1]
            content = content.replace(last_import, f"{last_import}\n{import_stmt}")
        else:
            content = f"{import_stmt}\n{content}"

    # Replace all catch blocks. We want to replace:
    # } on DioException catch (e) { ... }
    # OR
    # } catch (e) { if (e is DioException) ... throw ... }
    # 
    # Since they all follow a similar pattern, let's use regex to find the try-catch blocks and replace the whole catch part.
    # Actually, a simpler regex to replace `} on DioException catch (e) { ... }` where `...` doesn't contain `try {` or `} on`:
    
    # Let's replace the common one-liner:
    pattern1 = r"\}\s*on DioException catch\s*\([^)]+\)\s*\{\s*throw e\.error is ApiException \? e\.error as ApiException : ApiException\(message: e\.message \?\? 'Error de red', statusCode: e\.response\?\.statusCode \?\? 500, type: ApiExceptionType\.network\);\s*\}"
    content = re.sub(pattern1, "} catch (e) {\n      throw ApiErrorHandler.handle(e);\n    }", content)

    # Multi-line version:
    pattern2 = r"\}\s*on DioException catch\s*\([^)]+\)\s*\{\s*throw e\.error is ApiException\s*\?\s*e\.error as ApiException\s*:\s*ApiException\(\s*message:\s*e\.message \?\? 'Error de red',\s*statusCode:\s*e\.response\?\.statusCode \?\? 500,\s*type:\s*ApiExceptionType\.network,\s*\);\s*\}"
    content = re.sub(pattern2, "} catch (e) {\n      throw ApiErrorHandler.handle(e);\n    }", content)

    # If there are still `on DioException`, let's just replace them blindly because we want ALL errors handled by ApiErrorHandler:
    # We replace:
    # } on DioException catch (e) {
    #   [ANYTHING UNTIL the next method or end of try block]
    # Since dart brackets are hard to parse with regex, let's just do a naive substitution for the exact strings.
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"No changes in {filepath}")

def main():
    repo_dir = '../app_condominio/lib/features'
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('_repository.dart'):
                process_file(os.path.join(root, file))

if __name__ == '__main__':
    main()
