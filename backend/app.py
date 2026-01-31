import os
import json
import uuid
import shutil
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import threading

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

class RahlAIBuilder:
    def __init__(self):
        self.projects = {}
        self.load_templates()
        
    def load_templates(self):
        """Load available app templates"""
        self.templates = {
            'calculator': {
                'name': 'Calculator',
                'description': 'A simple calculator app with basic operations',
                'icon': '🧮',
                'complexity': 'simple'
            },
            'webview': {
                'name': 'WebView App',
                'description': 'An Android app that displays a website',
                'icon': '🌐',
                'complexity': 'simple'
            },
            'todo': {
                'name': 'Todo List',
                'description': 'A simple todo list app',
                'icon': '✅',
                'complexity': 'medium'
            },
            'notes': {
                'name': 'Notes App',
                'description': 'A note-taking application',
                'icon': '📝',
                'complexity': 'medium'
            },
            'weather': {
                'name': 'Weather App',
                'description': 'A weather forecast application',
                'icon': '⛅',
                'complexity': 'advanced'
            },
            'game': {
                'name': 'Simple Game',
                'description': 'A basic game like tic-tac-toe',
                'icon': '🎮',
                'complexity': 'advanced'
            }
        }
        
    def analyze_description(self, description):
        """Analyze natural language description to determine app type and features"""
        description_lower = description.lower()
        
        # Keywords for different app types
        keywords = {
            'calculator': ['calculator', 'calculate', 'math', 'arithmetic', 'add', 'subtract'],
            'webview': ['website', 'web', 'http', 'blog', 'site', 'browser'],
            'todo': ['todo', 'to-do', 'task', 'checklist', 'reminder', 'schedule'],
            'notes': ['note', 'notepad', 'write', 'journal', 'diary'],
            'weather': ['weather', 'forecast', 'temperature', 'climate'],
            'game': ['game', 'play', 'fun', 'entertain', 'tic-tac-toe', 'puzzle']
        }
        
        # Determine app type based on keywords
        app_type = 'webview'  # default
        
        for template_type, kw_list in keywords.items():
            for keyword in kw_list:
                if keyword in description_lower:
                    app_type = template_type
                    break
        
        # Extract features
        features = []
        if 'dark' in description_lower or 'dark mode' in description_lower:
            features.append('dark_mode')
        if 'notification' in description_lower:
            features.append('notifications')
        if 'database' in description_lower or 'store' in description_lower or 'save' in description_lower:
            features.append('database')
        if 'share' in description_lower:
            features.append('sharing')
        if 'login' in description_lower or 'sign in' in description_lower:
            features.append('authentication')
            
        # Generate package name
        words = description_lower.split()[:3]
        package_name = f"com.rahl.{'.'.join(words)}".replace(' ', '_').lower()[:50]
        
        return {
            'app_type': app_type,
            'features': features,
            'package_name': package_name,
            'detected_features': len(features)
        }
    
    def create_project(self, project_id, app_type, package_name, features, description):
        """Create a new Android project"""
        project_path = os.path.join(PROJECTS_DIR, project_id)
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create project metadata
        metadata = {
            'id': project_id,
            'app_type': app_type,
            'package_name': package_name,
            'features': features,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'status': 'building',
            'progress': 0
        }
        
        # Save metadata
        with open(os.path.join(project_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create Android project structure
        self.generate_android_project(project_path, app_type, package_name, features)
        
        # Update status
        metadata['status'] = 'generated'
        metadata['progress'] = 50
        
        with open(os.path.join(project_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return project_path
    
    def generate_android_project(self, project_path, app_type, package_name, features):
        """Generate Android project files"""
        # Create basic Android structure
        src_dir = os.path.join(project_path, 'app', 'src', 'main')
        os.makedirs(os.path.join(src_dir, 'java', *package_name.split('.')), exist_ok=True)
        os.makedirs(os.path.join(src_dir, 'res', 'layout'), exist_ok=True)
        os.makedirs(os.path.join(src_dir, 'res', 'values'), exist_ok=True)
        os.makedirs(os.path.join(src_dir, 'res', 'drawable'), exist_ok=True)
        
        # Generate AndroidManifest.xml
        self.generate_manifest(project_path, package_name, app_type)
        
        # Generate MainActivity.java based on app type
        self.generate_main_activity(project_path, package_name, app_type, features)
        
        # Generate layout files
        self.generate_layouts(project_path, app_type)
        
        # Generate build.gradle
        self.generate_build_gradle(project_path, package_name)
        
        # Generate string resources
        self.generate_strings(project_path, app_type)
        
        # Create dummy APK for now (we'll replace with real build later)
        self.create_dummy_apk(project_path)
    
    def generate_manifest(self, project_path, package_name, app_type):
        """Generate AndroidManifest.xml"""
        manifest_content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    
    <uses-permission android:name="android.permission.INTERNET" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.RahlApp">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""
        
        manifest_path = os.path.join(project_path, 'app', 'src', 'main', 'AndroidManifest.xml')
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        
        with open(manifest_path, 'w') as f:
            f.write(manifest_content)
    
    def generate_main_activity(self, project_path, package_name, app_type, features):
        """Generate MainActivity.java based on app type"""
        # Create package directory structure
        package_path = package_name.replace('.', '/')
        java_dir = os.path.join(project_path, 'app', 'src', 'main', 'java', package_path)
        os.makedirs(java_dir, exist_ok=True)
        
        if app_type == 'calculator':
            activity_content = f"""package {package_name};

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{
    
    private TextView display;
    private String currentNumber = "";
    private String operation = "";
    private double firstNumber = 0;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        display = findViewById(R.id.display);
        
        // Number buttons
        int[] numberButtons = {{
            R.id.btn_0, R.id.btn_1, R.id.btn_2, R.id.btn_3, R.id.btn_4,
            R.id.btn_5, R.id.btn_6, R.id.btn_7, R.id.btn_8, R.id.btn_9
        }};
        
        for (int id : numberButtons) {{
            findViewById(id).setOnClickListener(v -> {{
                Button btn = (Button) v;
                currentNumber += btn.getText().toString();
                display.setText(currentNumber);
            }});
        }}
        
        // Operation buttons
        findViewById(R.id.btn_add).setOnClickListener(v -> performOperation("+"));
        findViewById(R.id.btn_subtract).setOnClickListener(v -> performOperation("-"));
        findViewById(R.id.btn_multiply).setOnClickListener(v -> performOperation("*"));
        findViewById(R.id.btn_divide).setOnClickListener(v -> performOperation("/"));
        
        findViewById(R.id.btn_equals).setOnClickListener(v -> calculateResult());
        findViewById(R.id.btn_clear).setOnClickListener(v -> clearAll());
    }}
    
    private void performOperation(String op) {{
        if (!currentNumber.isEmpty()) {{
            firstNumber = Double.parseDouble(currentNumber);
            operation = op;
            currentNumber = "";
            display.setText(op);
        }}
    }}
    
    private void calculateResult() {{
        if (!currentNumber.isEmpty() && !operation.isEmpty()) {{
            double secondNumber = Double.parseDouble(currentNumber);
            double result = 0;
            
            switch (operation) {{
                case "+": result = firstNumber + secondNumber; break;
                case "-": result = firstNumber - secondNumber; break;
                case "*": result = firstNumber * secondNumber; break;
                case "/": result = firstNumber / secondNumber; break;
            }}
            
            display.setText(String.valueOf(result));
            currentNumber = String.valueOf(result);
            operation = "";
        }}
    }}
    
    private void clearAll() {{
        currentNumber = "";
        operation = "";
        firstNumber = 0;
        display.setText("0");
    }}
}}"""
        
        elif app_type == 'webview':
            # Extract URL from description if possible
            activity_content = f"""package {package_name};

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{
    
    private WebView webView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        webView = findViewById(R.id.webview);
        webView.setWebViewClient(new WebViewClient());
        webView.getSettings().setJavaScriptEnabled(true);
        webView.loadUrl("https://github.com");
    }}
    
    @Override
    public void onBackPressed() {{
        if (webView.canGoBack()) {{
            webView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}
}}"""
        
        elif app_type == 'todo':
            activity_content = f"""package {package_name};

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import androidx.appcompat.app.AppCompatActivity;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {{
    
    private List<String> todoItems;
    private TodoAdapter adapter;
    private EditText inputField;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        todoItems = new ArrayList<>();
        adapter = new TodoAdapter(this, todoItems);
        
        ListView listView = findViewById(R.id.todo_list);
        listView.setAdapter(adapter);
        
        inputField = findViewById(R.id.todo_input);
        Button addButton = findViewById(R.id.btn_add);
        
        addButton.setOnClickListener(v -> {{
            String newItem = inputField.getText().toString().trim();
            if (!newItem.isEmpty()) {{
                todoItems.add(newItem);
                adapter.notifyDataSetChanged();
                inputField.setText("");
            }}
        }});
        
        listView.setOnItemClickListener((parent, view, position, id) -> {{
            todoItems.remove(position);
            adapter.notifyDataSetChanged();
        }});
    }}
}}

class TodoAdapter extends android.widget.ArrayAdapter<String> {{
    
    public TodoAdapter(MainActivity context, List<String> items) {{
        super(context, android.R.layout.simple_list_item_1, items);
    }}
}}"""
        
        else:  # Default simple app
            activity_content = f"""package {package_name};

import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        TextView textView = findViewById(R.id.textView);
        textView.setText("Welcome to your {app_type} app!");
        
        // Add feature-specific code
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {{
            // Dark mode support
            getDelegate().setLocalNightMode(
                android.content.res.Configuration.UI_MODE_NIGHT_YES);
        }}
    }}
}}"""
        
        activity_path = os.path.join(java_dir, 'MainActivity.java')
        with open(activity_path, 'w') as f:
            f.write(activity_content)
    
    def generate_layouts(self, project_path, app_type):
        """Generate layout XML files"""
        layout_dir = os.path.join(project_path, 'app', 'src', 'main', 'res', 'layout')
        os.makedirs(layout_dir, exist_ok=True)
        
        if app_type == 'calculator':
            layout_content = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">
    
    <TextView
        android:id="@+id/display"
        android:layout_width="match_parent"
        android:layout_height="80dp"
        android:text="0"
        android:textSize="32sp"
        android:gravity="end|center_vertical"
        android:background="#f0f0f0"
        android:padding="16dp" />
    
    <GridLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:columnCount="4"
        android:rowCount="5">
        
        <!-- Row 1 -->
        <Button android:id="@+id/btn_clear" android:text="C" style="@style/CalcButton" />
        <Button android:id="@+id/btn_divide" android:text="/" style="@style/CalcButton" />
        <Button android:id="@+id/btn_multiply" android:text="*" style="@style/CalcButton" />
        <Button android:id="@+id/btn_backspace" android:text="⌫" style="@style/CalcButton" />
        
        <!-- Row 2 -->
        <Button android:id="@+id/btn_7" android:text="7" style="@style/CalcButton" />
        <Button android:id="@+id/btn_8" android:text="8" style="@style/CalcButton" />
        <Button android:id="@+id/btn_9" android:text="9" style="@style/CalcButton" />
        <Button android:id="@+id/btn_subtract" android:text="-" style="@style/CalcButton" />
        
        <!-- Row 3 -->
        <Button android:id="@+id/btn_4" android:text="4" style="@style/CalcButton" />
        <Button android:id="@+id/btn_5" android:text="5" style="@style/CalcButton" />
        <Button android:id="@+id/btn_6" android:text="6" style="@style/CalcButton" />
        <Button android:id="@+id/btn_add" android:text="+" style="@style/CalcButton" />
        
        <!-- Row 4 -->
        <Button android:id="@+id/btn_1" android:text="1" style="@style/CalcButton" />
        <Button android:id="@+id/btn_2" android:text="2" style="@style/CalcButton" />
        <Button android:id="@+id/btn_3" android:text="3" style="@style/CalcButton" />
        <Button android:id="@+id/btn_equals" android:text="=" 
            android:layout_rowSpan="2" style="@style/CalcButton" />
        
        <!-- Row 5 -->
        <Button android:id="@+id/btn_0" android:text="0" 
            android:layout_columnSpan="2" style="@style/CalcButton" />
        <Button android:id="@+id/btn_dot" android:text="." style="@style/CalcButton" />
        
    </GridLayout>
</LinearLayout>"""
            
            # Create styles file
            styles_dir = os.path.join(project_path, 'app', 'src', 'main', 'res', 'values')
            os.makedirs(styles_dir, exist_ok=True)
            
            styles_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="CalcButton">
        <item name="android:layout_width">0dp</item>
        <item name="android:layout_height">80dp</item>
        <item name="android:layout_columnWeight">1</item>
        <item name="android:layout_rowWeight">1</item>
        <item name="android:textSize">24sp</item>
        <item name="android:backgroundTint">#6200EE</item>
        <item name="android:textColor">#FFFFFF</item>
    </style>
</resources>"""
            
            styles_path = os.path.join(styles_dir, 'styles.xml')
            with open(styles_path, 'w') as f:
                f.write(styles_content)
        
        elif app_type == 'webview':
            layout_content = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">
    
    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
    
</LinearLayout>"""
        
        elif app_type == 'todo':
            layout_content = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">
    
    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Todo List"
        android:textSize="24sp"
        android:textStyle="bold"
        android:gravity="center"
        android:padding="16dp" />
    
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal">
        
        <EditText
            android:id="@+id/todo_input"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:hint="Enter todo item"
            android:padding="12dp" />
        
        <Button
            android:id="@+id/btn_add"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Add"
            android:padding="12dp" />
    </LinearLayout>
    
    <ListView
        android:id="@+id/todo_list"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:padding="8dp" />
    
</LinearLayout>"""
        
        else:
            layout_content = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center"
    android:padding="24dp">
    
    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello Rahl AI!"
        android:textSize="24sp"
        android:textStyle="bold" />
    
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Your app is ready!"
        android:textSize="18sp"
        android:layout_marginTop="16dp" />
    
</LinearLayout>"""
        
        layout_path = os.path.join(layout_dir, 'activity_main.xml')
        with open(layout_path, 'w') as f:
            f.write(layout_content)
    
    def generate_build_gradle(self, project_path, package_name):
        """Generate build.gradle files"""
        # Main app build.gradle
        app_build_gradle = """plugins {
    id 'com.android.application'
}

android {
    namespace '%s'
    compileSdk 34
    
    defaultConfig {
        applicationId "%s"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
    
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.10.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}""" % (package_name, package_name)
        
        app_build_path = os.path.join(project_path, 'app', 'build.gradle')
        os.makedirs(os.path.dirname(app_build_path), exist_ok=True)
        with open(app_build_path, 'w') as f:
            f.write(app_build_gradle)
        
        # Project build.gradle
        project_build_gradle = """plugins {
    id 'com.android.application' version '8.1.0' apply false
}"""
        
        project_build_path = os.path.join(project_path, 'build.gradle')
        with open(project_build_path, 'w') as f:
            f.write(project_build_gradle)
        
        # settings.gradle
        settings_gradle = """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "RahlApp"
include ':app'"""
        
        settings_path = os.path.join(project_path, 'settings.gradle')
        with open(settings_path, 'w') as f:
            f.write(settings_gradle)
        
        # gradle.properties
        gradle_props = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true"""
        
        props_path = os.path.join(project_path, 'gradle.properties')
        with open(props_path, 'w') as f:
            f.write(gradle_props)
    
    def generate_strings(self, project_path, app_type):
        """Generate string resources"""
        strings_dir = os.path.join(project_path, 'app', 'src', 'main', 'res', 'values')
        os.makedirs(strings_dir, exist_ok=True)
        
        app_names = {
            'calculator': 'Rahl Calculator',
            'webview': 'Rahl Browser',
            'todo': 'Rahl Todo',
            'notes': 'Rahl Notes',
            'weather': 'Rahl Weather',
            'game': 'Rahl Game'
        }
        
        app_name = app_names.get(app_type, 'Rahl App')
        
        strings_content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_name}</string>
    <string name="hello_world">Hello from Rahl AI!</string>
</resources>"""
        
        strings_path = os.path.join(strings_dir, 'strings.xml')
        with open(strings_path, 'w') as f:
            f.write(strings_content)
    
    def create_dummy_apk(self, project_path):
        """Create a dummy APK file (for demo purposes)"""
        apk_dir = os.path.join(project_path, 'app', 'build', 'outputs', 'apk', 'debug')
        os.makedirs(apk_dir, exist_ok=True)
        
        dummy_apk_path = os.path.join(apk_dir, 'app-debug.apk')
        
        # Create a text file that looks like an APK (for demo)
        dummy_content = """Rahl AI - Generated APK
========================
This is a demo APK generated by Rahl AI Builder.

For a real APK, you need to:
1. Install Android SDK
2. Set up Gradle
3. Build with: ./gradlew assembleDebug

But for this demo, we're showing the process!

Your app has been successfully analyzed and the code generated.

Check the project folder for complete Android source code."""
        
        with open(dummy_apk_path, 'w') as f:
            f.write(dummy_content)
    
    def build_project_thread(self, project_id, analysis):
        """Thread function to build project"""
        try:
            project_path = self.create_project(
                project_id, 
                analysis['app_type'], 
                analysis['package_name'], 
                analysis['features'], 
                ""
            )
            
            # Update project status
            metadata_path = os.path.join(project_path, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                metadata['status'] = 'completed'
                metadata['progress'] = 100
                metadata['apk_path'] = os.path.join(project_path, 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk')
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            print(f"✅ Project {project_id} built successfully")
            
        except Exception as e:
            print(f"❌ Error building project {project_id}: {str(e)}")
            
            # Update with error status
            project_path = os.path.join(PROJECTS_DIR, project_id)
            metadata_path = os.path.join(project_path, 'metadata.json')
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                metadata['status'] = 'error'
                metadata['error'] = str(e)
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)

# Initialize the builder
builder = RahlAIBuilder()

# API Routes
@app.route('/')
def home():
    return jsonify({
        'service': 'Rahl AI APK Builder',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            '/': 'This info',
            '/api/templates': 'Get available templates',
            '/api/build': 'POST: Build APK from description',
            '/api/project/<id>': 'GET: Get project status',
            '/api/download/<id>': 'GET: Download APK'
        }
    })

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all available app templates"""
    return jsonify({
        'templates': builder.templates,
        'count': len(builder.templates)
    })

@app.route('/api/build', methods=['POST'])
def build_apk():
    """Main endpoint: Build APK from natural language description"""
    try:
        data = request.json
        if not data or 'description' not in data:
            return jsonify({'error': 'Missing description'}), 400
        
        description = data['description'].strip()
        if len(description) < 5:
            return jsonify({'error': 'Description too short'}), 400
        
        # Generate project ID
        project_id = str(uuid.uuid4())[:8]
        
        # Analyze description
        analysis = builder.analyze_description(description)
        
        # Start build in background thread
        thread = threading.Thread(
            target=builder.build_project_thread,
            args=(project_id, analysis)
        )
        thread.daemon = True
        thread.start()
        
        # Return immediate response
        return jsonify({
            'status': 'building',
            'project_id': project_id,
            'analysis': analysis,
            'message': 'Your APK is being built in the background',
            'check_status': f'/api/project/{project_id}',
            'download': f'/api/download/{project_id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/<project_id>', methods=['GET'])
def get_project_status(project_id):
    """Get project build status"""
    project_path = os.path.join(PROJECTS_DIR, project_id)
    metadata_path = os.path.join(project_path, 'metadata.json')
    
    if not os.path.exists(metadata_path):
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Check if APK exists
        apk_path = metadata.get('apk_path')
        if apk_path and os.path.exists(apk_path):
            metadata['apk_ready'] = True
            metadata['apk_size'] = os.path.getsize(apk_path)
        else:
            metadata['apk_ready'] = False
        
        return jsonify(metadata)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<project_id>', methods=['GET'])
def download_apk(project_id):
    """Download the generated APK"""
    project_path = os.path.join(PROJECTS_DIR, project_id)
    apk_path = os.path.join(project_path, 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk')
    
    if os.path.exists(apk_path):
        return send_file(
            apk_path,
            as_attachment=True,
            download_name=f'rahl_{project_id}.apk',
            mimetype='application/vnd.android.package-archive'
        )
    
    # Fallback: Check metadata for APK path
    metadata_path = os.path.join(project_path, 'metadata.json')
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        fallback_apk = metadata.get('apk_path')
        if fallback_apk and os.path.exists(fallback_apk):
            return send_file(
                fallback_apk,
                as_attachment=True,
                download_name=f'rahl_{project_id}.apk'
            )
    
    return jsonify({'error': 'APK not found or not built yet'}), 404

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    projects = []
    
    if os.path.exists(PROJECTS_DIR):
        for project_id in os.listdir(PROJECTS_DIR):
            project_path = os.path.join(PROJECTS_DIR, project_id)
            metadata_path = os.path.join(project_path, 'metadata.json')
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    projects.append({
                        'id': project_id,
                        'app_type': metadata.get('app_type'),
                        'status': metadata.get('status'),
                        'created_at': metadata.get('created_at')
                    })
                except:
                    continue
    
    return jsonify({
        'projects': projects,
        'count': len(projects)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_description():
    """Analyze description without building"""
    data = request.json
    if not data or 'description' not in data:
        return jsonify({'error': 'Missing description'}), 400
    
    description = data['description'].strip()
    analysis = builder.analyze_description(description)
    
    return jsonify({
        'analysis': analysis,
        'description': description,
        'suggested_templates': [builder.templates.get(analysis['app_type'])]
    })

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Rahl AI APK Builder...")
    print(f"📁 Projects directory: {PROJECTS_DIR}")
    print(f"📁 Templates directory: {TEMPLATES_DIR}")
    print("🌐 Server running on http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
