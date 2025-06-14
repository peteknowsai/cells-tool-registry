#!/usr/bin/env python3
"""
Echo Tool - A versatile command-line echo utility with formatting options
"""

import argparse
import sys
import json
import time
import os
from typing import Optional, List, Dict, Any


class EchoTool:
    """Main echo tool implementation"""
    
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description='Echo text with various formatting options and transformations',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  echo-tool "Hello World"                          # Basic echo
  echo-tool "hello" --upper                        # Uppercase
  echo-tool "Important" --repeat 3 --prefix ">>> " # Repeat with prefix
  echo-tool "Notice" --box                         # ASCII box
  echo-tool "data" --json                          # JSON output
  echo "piped text" | echo-tool --upper            # Accept piped input
            """
        )
        
        # Positional argument
        parser.add_argument('text', nargs='?', help='Text to echo (optional if piped)')
        
        # Transformation options
        transform_group = parser.add_argument_group('transformations')
        transform_group.add_argument('-u', '--upper', action='store_true',
                                   help='Convert to uppercase')
        transform_group.add_argument('-l', '--lower', action='store_true',
                                   help='Convert to lowercase')
        transform_group.add_argument('-t', '--title', action='store_true',
                                   help='Convert to title case')
        transform_group.add_argument('-r', '--reverse', action='store_true',
                                   help='Reverse the text')
        
        # Formatting options
        format_group = parser.add_argument_group('formatting')
        format_group.add_argument('-p', '--prefix', type=str, default='',
                                help='Add prefix to output')
        format_group.add_argument('-s', '--suffix', type=str, default='',
                                help='Add suffix to output')
        format_group.add_argument('-n', '--repeat', type=int, default=1,
                                help='Repeat output n times (default: 1)')
        format_group.add_argument('--line-numbers', action='store_true',
                                help='Add line numbers to output')
        
        # Output options
        output_group = parser.add_argument_group('output')
        output_group.add_argument('-o', '--output', type=str,
                                help='Output to file')
        output_group.add_argument('-a', '--append', type=str,
                                help='Append to file')
        output_group.add_argument('--json', action='store_true',
                                help='Output in JSON format')
        
        # Special features
        special_group = parser.add_argument_group('special features')
        special_group.add_argument('--rainbow', action='store_true',
                                 help='Rainbow color effect (requires terminal support)')
        special_group.add_argument('--box', action='store_true',
                                 help='Wrap text in ASCII art box')
        special_group.add_argument('--type', action='store_true',
                                 help='Simulate typing effect')
        special_group.add_argument('--count', action='store_true',
                                 help='Show word and character count')
        
        return parser
    
    def get_input_text(self, args) -> str:
        """Get input text from arguments or stdin"""
        if args.text is not None:  # Check explicitly for None, not falsy
            return args.text
        elif not sys.stdin.isatty():
            return sys.stdin.read().strip()
        else:
            self.parser.error("No input text provided. Use positional argument or pipe input.")
            
    def apply_transformations(self, text: str, args) -> str:
        """Apply text transformations based on arguments"""
        if args.upper:
            text = text.upper()
        elif args.lower:
            text = text.lower()
        elif args.title:
            text = text.title()
            
        if args.reverse:
            text = text[::-1]
            
        return text
    
    def apply_formatting(self, text: str, args) -> List[str]:
        """Apply formatting options and return list of lines"""
        lines = []
        
        # Split into lines for line number support
        text_lines = text.split('\n')
        
        for i in range(args.repeat):
            for j, line in enumerate(text_lines):
                formatted_line = f"{args.prefix}{line}{args.suffix}"
                
                if args.line_numbers:
                    line_num = i * len(text_lines) + j + 1
                    formatted_line = f"{line_num}: {formatted_line}"
                    
                lines.append(formatted_line)
                
        return lines
    
    def create_box(self, lines: List[str]) -> List[str]:
        """Wrap lines in an ASCII art box"""
        if not lines:
            return lines
            
        max_len = max(len(line) for line in lines)
        box_lines = []
        
        # Top border
        box_lines.append('┌' + '─' * (max_len + 2) + '┐')
        
        # Content
        for line in lines:
            padded = line.ljust(max_len)
            box_lines.append(f'│ {padded} │')
            
        # Bottom border
        box_lines.append('└' + '─' * (max_len + 2) + '┘')
        
        return box_lines
    
    def apply_rainbow(self, text: str) -> str:
        """Apply rainbow colors using ANSI escape codes"""
        colors = [
            '\033[91m',  # Red
            '\033[93m',  # Yellow
            '\033[92m',  # Green
            '\033[96m',  # Cyan
            '\033[94m',  # Blue
            '\033[95m',  # Magenta
        ]
        
        result = []
        for i, char in enumerate(text):
            if char != ' ':
                color = colors[i % len(colors)]
                result.append(f"{color}{char}\033[0m")
            else:
                result.append(char)
                
        return ''.join(result)
    
    def type_effect(self, text: str, delay: float = 0.05):
        """Simulate typing effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write('\n')
        sys.stdout.flush()
    
    def get_counts(self, text: str) -> Dict[str, int]:
        """Get word and character counts"""
        return {
            'characters': len(text),
            'characters_no_spaces': len(text.replace(' ', '').replace('\n', '')),
            'words': len(text.split()),
            'lines': len(text.split('\n'))
        }
    
    def output_result(self, lines: List[str], args, original_text: str):
        """Output the result based on arguments"""
        if args.json:
            result = {
                'input': original_text,
                'output': '\n'.join(lines),
                'transformations': {
                    'upper': args.upper,
                    'lower': args.lower,
                    'title': args.title,
                    'reverse': args.reverse
                },
                'formatting': {
                    'prefix': args.prefix,
                    'suffix': args.suffix,
                    'repeat': args.repeat,
                    'line_numbers': args.line_numbers
                }
            }
            
            if args.count:
                result['counts'] = self.get_counts(original_text)
                
            print(json.dumps(result, indent=2))
            
        else:
            # Apply special effects
            output_lines = lines[:]
            
            if args.box:
                output_lines = self.create_box(output_lines)
                
            # Determine output destination
            output_file = None
            mode = 'w'
            
            if args.output:
                output_file = args.output
            elif args.append:
                output_file = args.append
                mode = 'a'
                
            # Output the result
            if output_file:
                with open(output_file, mode) as f:
                    for line in output_lines:
                        f.write(line + '\n')
                print(f"Output {'written' if mode == 'w' else 'appended'} to {output_file}")
            else:
                for line in output_lines:
                    if args.rainbow and not args.type:
                        print(self.apply_rainbow(line))
                    elif args.type:
                        if args.rainbow:
                            line = self.apply_rainbow(line)
                        self.type_effect(line)
                    else:
                        print(line)
                        
            # Show counts if requested
            if args.count and not args.json:
                counts = self.get_counts(original_text)
                print(f"\n--- Statistics ---")
                print(f"Characters: {counts['characters']}")
                print(f"Characters (no spaces): {counts['characters_no_spaces']}")
                print(f"Words: {counts['words']}")
                print(f"Lines: {counts['lines']}")
    
    def run(self, argv: Optional[List[str]] = None):
        """Run the echo tool"""
        args = self.parser.parse_args(argv)
        
        # Get input text
        original_text = self.get_input_text(args)
        
        # Apply transformations
        transformed_text = self.apply_transformations(original_text, args)
        
        # Apply formatting
        formatted_lines = self.apply_formatting(transformed_text, args)
        
        # Output result
        self.output_result(formatted_lines, args, original_text)


def main():
    """Main entry point"""
    tool = EchoTool()
    try:
        tool.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()