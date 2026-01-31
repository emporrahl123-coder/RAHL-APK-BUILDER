# app.py - Main backend server
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

class RahlBuilder:
    def __init__(self):
        self.projects = {}
        self.templates = self.load_templates()
    
    def load_templates(self):
        return {
            'webview': {
                'name': 'WebView App',
                'description': 'Creates an Android app that displays a website',
                'template_path': 'templates/webview'
            },
            'calculator': {
                'name': 'Calculator',
                'description': 'Simple calculator application',
                'template_path': 'templates/calculator'
            },
            'notes': {
                'name': 'Notes App',
                'description': 'Note-taking application',
                'template_path': 'templates/notes'
            }
        }
    
    def analyze_intent(self, natural_language):
        """Analyze user's natural language input"""
        # This would integrate with an AI service (OpenAI, Claude, etc.)
        intent = {
            'app_type': self.detect_app_type(natural_language),
            'features': self.extract_features(natural_language),
            'design': self.extract_design_preferences(natural_language),
            'package_name': self.generate_package_name(natural_language)
        }
        return intent
    
    def detect_app_type(self, text):
        text_lower = text.lower()
        if 'calculator' in text_lower:
            return 'calculator'
        elif 'note' in text_lower or 'todo' in text_lower:
            return 'notes'
        elif 'website' in text_lower or 'web' in text_lower:
            return 'webview'
        elif 'game' in text_lower:
            return 'game'
        else:
            return 'webview'  # default
    
    def generate_project(self, intent, project_id):
        """Generate Android project structure"""
        project_dir = f'projects/{project_id}'
        os.makedirs(project_dir, exist_ok=True)
        
        # Copy template
        template = self.templates.get(intent['app_type'], self.templates['webview'])
        self.copy_template(template['template_path'], project_dir)
        
        # Customize based on intent
        self.customize_project(project_dir, intent)
        
        # Build APK
        apk_path = self.build_apk(project_dir, project_id)
        
        return {
            'project_id': project_id,
            'apk_path': apk_path,
            'download_url': f'/download/{project_id}',
            'status': 'completed'
        }
    
    def customize_project(self, project_dir, intent):
        """Customize the Android project based on user requirements"""
        manifest_path = os.path.join(project_dir, 'app/src/main/AndroidManifest.xml')
        
        # Update package name
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                content = f.read()
            
            # Replace package name
            content = content.replace('com.rahl.template', intent.get('package_name', 'com.rahl.app'))
            
            with open(manifest_path, 'w') as f:
                f.write(content)

builder = RahlBuilder()

@app.route('/api/build', methods=['POST'])
def build_apk():
    data = request.json
    natural_language = data.get('description', '')
    project_id = str(uuid.uuid4())
    
    # Analyze intent from natural language
    intent = builder.analyze_intent(natural_language)
    
    # Generate project
    result = builder.generate_project(intent, project_id)
    
    return jsonify(result)

@app.route('/api/templates', methods=['GET'])
def get_templates():
    return jsonify(builder.templates)

@app.route('/download/<project_id>', methods=['GET'])
def download_apk(project_id):
    apk_path = f'projects/{project_id}/app/build/outputs/apk/debug/app-debug.apk'
    if os.path.exists(apk_path):
        return send_file(apk_path, as_attachment=True)
    return jsonify({'error': 'APK not found'}), 404

if __name__ == '__main__':
    os.makedirs('projects', exist_ok=True)
    app.run(debug=True, port=5000)
