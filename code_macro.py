#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG: File Watcher Macro - Lots of debug output
"""

import FreeCAD as App
import FreeCADGui as Gui
import os
import sys
import subprocess
import threading
import time
from PySide2 import QtCore

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    print("✓ Watchdog imported successfully")
except ImportError as e:
    WATCHDOG_AVAILABLE = False
    print(f"✗ Watchdog import failed: {e}")

# Global variables
observer = None
polling_thread = None
reloader = None

class ThreadSafeReloader(QtCore.QObject):
    """Thread-safe geometry reloader with debug output"""
    
    reload_signal = QtCore.Signal(str)
    
    def __init__(self):
        super().__init__()
        self.reload_signal.connect(self.reload_geometry_safe)
        print("✓ ThreadSafeReloader created and signal connected")
    
    def request_reload(self, python_file_path):
        """Request a reload from any thread"""
        print(f"🔄 RELOAD REQUESTED: {python_file_path}")
        print(f"   Thread: {threading.current_thread().name}")
        self.reload_signal.emit(python_file_path)
        print("   Signal emitted")
    
    def reload_geometry_safe(self, python_file_path):
        """This runs on the main thread"""
        print(f"🎯 RELOAD EXECUTING ON MAIN THREAD: {python_file_path}")
        print(f"   Thread: {threading.current_thread().name}")
        
        try:
            # Check if file exists and is readable
            if not os.path.exists(python_file_path):
                print(f"✗ File does not exist: {python_file_path}")
                return
            
            print(f"✓ File exists, reading...")
            with open(python_file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print(f"✓ Read {len(code)} characters")
            
            # Create namespace
            namespace = {
                'App': App,
                'Gui': Gui,
                'FreeCAD': App,
                'FreeCADGui': Gui,
                '__file__': python_file_path,
                '__name__': '__main__'
            }
            
            # Add modules
            try:
                import Part
                namespace['Part'] = Part
                print("✓ Part module added")
            except ImportError:
                print("✗ Part module not available")
            
            print("🔧 Executing geometry code...")
            exec(code, namespace)
            print("✅ Code execution completed")
            
            # GUI updates
            if App.ActiveDocument:
                print("🔄 Recomputing document...")
                App.ActiveDocument.recompute()
                print("🖼️ Updating GUI...")
                Gui.updateGui()
                print("✅ RELOAD COMPLETE!")
                App.Console.PrintMessage(">>> Geometry updated from file! <<<\n")
            else:
                print("⚠️ No active document to recompute")
            
        except Exception as e:
            error_msg = f"💥 ERROR during reload: {str(e)}"
            print(error_msg)
            App.Console.PrintError(f"{error_msg}\n")
            import traceback
            traceback.print_exc()

class DebugFileHandler(FileSystemEventHandler):
    """File handler with extensive debug output"""
    
    def __init__(self, python_file_path):
        self.python_file_path = python_file_path
        self.last_modified = 0
        print(f"📁 FileHandler created for: {python_file_path}")
        
    def on_any_event(self, event):
        print(f"📂 FILE EVENT: {event.event_type} - {event.src_path}")
        
    def on_modified(self, event):
        print(f"✏️ MODIFIED EVENT: {event.src_path} (directory: {event.is_directory})")
        self._check_if_our_file_changed(event)
    
    def on_moved(self, event):
        print(f"📦 MOVED EVENT: {event.src_path} -> {event.dest_path}")
        # Check if a temp file was moved to our target file (atomic save)
        if hasattr(event, 'dest_path') and event.dest_path == self.python_file_path:
            print(f"🎯 TEMP FILE MOVED TO OUR FILE! (Atomic save detected)")
            self._trigger_reload()
        else:
            print(f"   Not our file (wanted: {self.python_file_path})")
    
    def _check_if_our_file_changed(self, event):
        """Check if this event affects our file"""
        if event.is_directory:
            print("   Ignoring directory event")
            return
            
        if event.src_path != self.python_file_path:
            print(f"   Not our file, ignoring (wanted: {self.python_file_path})")
            return
        
        print(f"🎯 OUR FILE WAS MODIFIED!")
        self._trigger_reload()
    
    def _trigger_reload(self):
        """Trigger a reload with debouncing"""
        # Debounce check
        current_time = time.time()
        time_diff = current_time - self.last_modified
        print(f"   Time since last: {time_diff:.2f}s")
        
        if time_diff < 1:
            print("   DEBOUNCED - too soon")
            return
            
        self.last_modified = current_time
        print(f"   Processing change...")
        
        # Request reload
        global reloader
        if reloader:
            reloader.request_reload(self.python_file_path)
        else:
            print("✗ No reloader available!")

class DebugPollingWatcher:
    """Polling watcher with debug output"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_modified = 0
        self.running = False
        print(f"🔍 PollingWatcher created for: {file_path}")
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._poll, name="GeometryPollingThread")
        self.thread.daemon = True
        self.thread.start()
        print(f"🔍 Polling thread started: {self.thread.name}")
        
    def stop(self):
        self.running = False
        print("🔍 Polling thread stop requested")
        
    def _poll(self):
        print(f"🔍 Polling loop started in thread: {threading.current_thread().name}")
        poll_count = 0
        
        while self.running:
            try:
                poll_count += 1
                if poll_count % 10 == 0:  # Every 10 seconds
                    print(f"🔍 Polling check #{poll_count}")
                
                if os.path.exists(self.file_path):
                    current_modified = os.path.getmtime(self.file_path)
                    if current_modified > self.last_modified:
                        if self.last_modified > 0:  # Skip first check
                            print(f"🔍 POLLING DETECTED CHANGE!")
                            print(f"   File: {self.file_path}")
                            print(f"   New mtime: {current_modified}")
                            print(f"   Old mtime: {self.last_modified}")
                            
                            global reloader
                            if reloader:
                                reloader.request_reload(self.file_path)
                            else:
                                print("✗ No reloader available!")
                        else:
                            print(f"🔍 Initial file check - mtime: {current_modified}")
                        self.last_modified = current_modified
                else:
                    print(f"⚠️ File does not exist: {self.file_path}")
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"💥 Polling error: {e}")
                time.sleep(1)
        
        print("🔍 Polling loop ended")

def start_debug_watcher(python_file_path):
    """Start file watcher with debug output"""
    global observer, polling_thread, reloader
    
    print(f"🚀 Starting file watcher for: {python_file_path}")
    
    # Create reloader
    reloader = ThreadSafeReloader()
    
    if WATCHDOG_AVAILABLE:
        try:
            print("📂 Trying watchdog observer...")
            event_handler = DebugFileHandler(python_file_path)
            observer = Observer()
            observer.schedule(event_handler, path=os.path.dirname(python_file_path), recursive=False)
            observer.start()
            print("✅ Watchdog observer started successfully!")
            return True
        except Exception as e:
            print(f"💥 Watchdog failed: {e}")
    
    # Fallback to polling
    print("🔍 Falling back to polling watcher...")
    polling_thread = DebugPollingWatcher(python_file_path)
    polling_thread.start()
    print("✅ Polling watcher started!")
    return True

def stop_debug_watcher():
    """Stop watchers"""
    global observer, polling_thread
    
    print("🛑 Stopping watchers...")
    
    if observer:
        observer.stop()
        observer.join()
        observer = None
        print("✅ Watchdog observer stopped")
    
    if polling_thread:
        polling_thread.stop()
        polling_thread = None
        print("✅ Polling watcher stopped")

def main():
    """Debug main function"""
    print("🚀 === DEBUG MACRO START ===")
    
    if not App.ActiveDocument or not App.ActiveDocument.FileName:
        print("✗ Need saved document")
        return
    
    # Get paths
    doc_path = App.ActiveDocument.FileName
    doc_dir = os.path.dirname(doc_path)
    doc_name = os.path.splitext(os.path.basename(doc_path))[0]
    python_file_path = os.path.join(doc_dir, doc_name + "_geometry.py")
    
    print(f"📄 Document: {doc_path}")
    print(f"🐍 Python file: {python_file_path}")
    print(f"📁 Directory writable: {os.access(doc_dir, os.W_OK)}")
    print(f"📄 Python file exists: {os.path.exists(python_file_path)}")
    
    if os.path.exists(python_file_path):
        mtime = os.path.getmtime(python_file_path)
        print(f"📅 File mtime: {mtime}")
    
    # Start watcher
    if start_debug_watcher(python_file_path):
        print("✅ Debug watcher started!")
        App.Console.PrintMessage("Debug file watcher is running. Check console for detailed output.\n")
        App.Console.PrintMessage("Edit and save the Python file to see debug messages.\n")
    
    print("🚀 === DEBUG MACRO COMPLETE ===")

# Cleanup
def cleanup():
    stop_debug_watcher()

import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    main()
