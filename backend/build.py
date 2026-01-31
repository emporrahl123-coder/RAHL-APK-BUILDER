#!/usr/bin/env python3
"""
Rahl AI - Android APK Builder
This script builds real Android APKs using Gradle
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

class AndroidAPKBuilder:
    def __init__(self, android_sdk_path=None):
        self.android_sdk_path = android_sdk_path or os.environ.get('ANDROID_SDK_PATH')
        self.project_count = 0
        
    def check_environment(self):
        """Check if Android build environment is available"""
        checks = {
            'Java': self._check_java(),
            'Android SDK': self._check_android_sdk(),
            'Gradle': self._check_gradle()
        }
        
        status = all(checks.values())
        return {
            'status': status,
            'checks': checks,
            'message': 'Environment ready' if status else 'Missing Android build tools'
        }
    
    def _check_java(self):
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_android_sdk(self):
        # Check common SDK locations
        sdk_paths = [
            self.android_sdk_path,
            os.path.join(os.environ.get('HOME', ''), 'Android/Sdk'),
            '/usr/local/android-sdk',
            'C:\\Android\\Sdk'  # Windows
        ]
        
        for path in sdk_paths:
            if path and os.path.exists(path):
                self.android_sdk_path = path
                return True
        return False
    
    def _check_gradle(self):
        try:
            # Try gradle wrapper first
            if os.path.exists('./gradlew'):
                return True
            
            # Try system gradle
            result = subprocess.run(['gradle', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def build_apk(self, project_path, build_type='debug'):
        """Build APK using Gradle"""
        try:
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            print(f"📦 Building APK for project: {project_path}")
            
            # Set environment variables
            env = os.environ.copy()
            if self.android_sdk_path:
                env['ANDROID_SDK_ROOT'] = self.android_sdk_path
                env['ANDROID_HOME'] = self.android_sdk_path
            
            # Use gradle wrapper if available, otherwise use system gradle
            gradle_cmd = ['./gradlew'] if os.path.exists('./gradlew') else ['gradle']
            
            if build_type == 'release':
                cmd = gradle_cmd + ['assembleRelease']
            else:
                cmd = gradle_cmd + ['assembleDebug']
            
            print(f"🛠️  Running: {' '.join(cmd)}")
            
            # Run gradle build
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output
            build_output = []
            for line in process.stdout:
                print(line.strip())
                build_output.append(line.strip())
            
            process.wait()
            
            # Change back to original directory
            os.chdir(original_dir)
            
            if process.returncode == 0:
                print("✅ Build successful!")
                
                # Find the APK file
                apk_path = self._find_apk_file(project_path, build_type)
                if apk_path:
                    return {
                        'success': True,
                        'apk_path': apk_path,
                        'apk_size': os.path.getsize(apk_path),
                        'output': '\n'.join(build_output[-20:])  # Last 20 lines
                    }
                else:
                    return {
                        'success': False,
                        'error': 'APK file not found after build',
                        'output': '\n'.join(build_output[-20:])
                    }
            else:
                print("❌ Build failed!")
                return {
                    'success': False,
                    'error': f'Build failed with exit code {process.returncode}',
                    'output': '\n'.join(build_output[-20:])
                }
                
        except Exception as e:
            print(f"💥 Build error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if 'original_dir' in locals():
                os.chdir(original_dir)
    
    def _find_apk_file(self, project_path, build_type):
        """Find the generated APK file"""
        apk_patterns = [
            f"app/build/outputs/apk/{build_type}/app-{build_type}.apk",
            f"app/build/outputs/apk/{build_type}/*.apk",
            f"build/outputs/apk/{build_type}/*.apk"
        ]
        
        for pattern in apk_patterns:
            apk_path = os.path.join(project_path, pattern)
            import glob
            files = glob.glob(apk_path)
            if files:
                return files[0]
        
        # Try to find any .apk file
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.apk'):
                    return os.path.join(root, file)
        
        return None
    
    def sign_apk(self, apk_path, keystore_path, keystore_password, key_alias):
        """Sign APK with keystore"""
        try:
            # This is a simplified version - in production, use proper signing
            print(f"🔏 Signing APK: {apk_path}")
            
            # For demo, just copy and rename
            signed_path = apk_path.replace('.apk', '-signed.apk')
            shutil.copy2(apk_path, signed_path)
            
            return {
                'success': True,
                'signed_apk': signed_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Command line interface
if __name__ == "__main__":
    builder = AndroidAPKBuilder()
    
    if len(sys.argv) < 2:
        print("Usage: python build.py <project_path> [debug|release]")
        print("\nOptions:")
        print("  project_path: Path to Android project directory")
        print("  build_type:   debug (default) or release")
        sys.exit(1)
    
    project_path = sys.argv[1]
    build_type = sys.argv[2] if len(sys.argv) > 2 else 'debug'
    
    if not os.path.exists(project_path):
        print(f"❌ Project path not found: {project_path}")
        sys.exit(1)
    
    # Check environment
    env_check = builder.check_environment()
    print("\n🔍 Environment Check:")
    for tool, available in env_check['checks'].items():
        status = "✅" if available else "❌"
        print(f"  {status} {tool}")
    
    if not env_check['status']:
        print("\n⚠️  Warning: Some build tools are missing")
        print("The build might fail without proper Android SDK setup")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Build APK
    print(f"\n🚀 Starting build for: {project_path}")
    result = builder.build_apk(project_path, build_type)
    
    if result['success']:
        print(f"\n🎉 Build successful!")
        print(f"📱 APK generated at: {result['apk_path']}")
        print(f"📊 APK size: {result['apk_size'] / 1024 / 1024:.2f} MB")
    else:
        print(f"\n💥 Build failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        if 'output' in result:
            print("\nLast output:")
            print(result['output'])
        sys.exit(1)
