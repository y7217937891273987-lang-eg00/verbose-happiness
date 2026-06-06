"""Main Window - Primary GUI application window"""

import logging
import PySimpleGUI as sg
from typing import Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Main application window using PySimpleGUI.
    
    Components:
    - Task submission panel
    - Real-time monitoring
    - Approval dialog integration
    - Status dashboard
    """

    def __init__(self, app_instance=None, theme: str = "DarkBlue3"):
        self.app = app_instance
        sg.theme(theme)
        self.window = None
        self.tasks_in_progress = {}
        logger.info(f"MainWindow initialized with theme: {theme}")

    def create_layout(self) -> list:
        """
        Create the main GUI layout.
        """
        layout = [
            # Header
            [
                sg.Text("🤖 Hybrid AI System", size=(30, 1), font=("Arial", 18, "bold")),
                sg.Push(),
                sg.Button("Settings", size=(10, 1)),
                sg.Button("Exit", size=(10, 1))
            ],
            [
                sg.HorizontalSeparator()
            ],
            
            # Main content area
            [
                # Left panel - Task submission
                sg.Column([
                    [
                        sg.Text("Task Description", font=("Arial", 11, "bold"))
                    ],
                    [
                        sg.Multiline(
                            size=(50, 8),
                            key="-TASK_INPUT-",
                            tooltip="Enter your task here",
                            pad=(5, 5)
                        )
                    ],
                    [
                        sg.Text("Task Type:"),
                        sg.Combo(
                            ["Auto-detect", "Research", "Code", "Business", "General"],
                            default_value="Auto-detect",
                            key="-TASK_TYPE-",
                            size=(20, 1)
                        )
                    ],
                    [
                        sg.Checkbox("Require Approval", default=True, key="-REQUIRE_APPROVAL-")
                    ],
                    [
                        sg.Button("Submit Task", size=(20, 2), button_color=("white", "green")),
                        sg.Button("Clear", size=(10, 2))
                    ]
                ], vertical_alignment="top", key="-TASK_PANEL-"),
                
                # Right panel - Status and monitoring
                sg.Column([
                    [
                        sg.Text("System Status", font=("Arial", 11, "bold"))
                    ],
                    [
                        sg.Multiline(
                            size=(50, 6),
                            key="-STATUS_OUTPUT-",
                            disabled=True,
                            autoscroll=True,
                            pad=(5, 5)
                        )
                    ],
                    [
                        sg.Text("Active Tasks: 0", key="-ACTIVE_TASKS-"),
                        sg.Push(),
                        sg.Text("LLM: Ollama", key="-LLM_STATUS-")
                    ],
                    [
                        sg.Button("View Logs", size=(15, 1)),
                        sg.Button("Clear Output", size=(15, 1))
                    ]
                ], vertical_alignment="top", key="-STATUS_PANEL-")
            ],
            
            [
                sg.HorizontalSeparator()
            ],
            
            # Bottom tabs
            [
                sg.TabGroup([
                    [
                        sg.Tab("Task History", [
                            [
                                sg.Listbox(
                                    values=[],
                                    size=(102, 6),
                                    key="-TASK_HISTORY-",
                                    tooltip="Previous tasks"
                                )
                            ]
                        ]),
                        sg.Tab("Audit Log", [
                            [
                                sg.Multiline(
                                    size=(102, 6),
                                    key="-AUDIT_LOG-",
                                    disabled=True,
                                    autoscroll=True
                                )
                            ]
                        ]),
                        sg.Tab("Agent Performance", [
                            [
                                sg.Multiline(
                                    size=(102, 6),
                                    key="-AGENT_PERF-",
                                    disabled=True
                                )
                            ]
                        ])
                    ]
                ])
            ]
        ]
        
        return layout

    def show(self) -> None:
        """
        Display the main window.
        """
        layout = self.create_layout()
        self.window = sg.Window(
            "Hybrid AI System - Phase 2",
            layout,
            size=(1200, 900),
            finalize=True,
            resizable=True
        )
        logger.info("Main window displayed")

    def get_task_input(self) -> str:
        """Get task input from text field"""
        return self.window["-TASK_INPUT-"].get()

    def clear_task_input(self) -> None:
        """Clear task input field"""
        self.window["-TASK_INPUT-"].update("")

    def update_status(self, message: str) -> None:
        """Update status output"""
        current = self.window["-STATUS_OUTPUT-"].get()
        self.window["-STATUS_OUTPUT-"].update(current + "\n" + message)

    def update_active_tasks(self, count: int) -> None:
        """Update active task count"""
        self.window["-ACTIVE_TASKS-"].update(f"Active Tasks: {count}")

    def update_audit_log(self, log_entries: list) -> None:
        """Update audit log display"""
        log_text = "\n".join([f"[{e['timestamp']}] {e['action_type']}: {e['description']}" for e in log_entries])
        self.window["-AUDIT_LOG-"].update(log_text)

    def run_event_loop(self):
        """
        Run the GUI event loop.
        """
        while True:
            event, values = self.window.read(timeout=1000)
            
            if event == sg.WINDOW_CLOSED or event == "Exit":
                break
            
            elif event == "Submit Task":
                task = self.get_task_input()
                if task:
                    asyncio.run(self._handle_task_submission(task, values))
            
            elif event == "Clear":
                self.clear_task_input()
            
            elif event == "Clear Output":
                self.window["-STATUS_OUTPUT-"].update("")
            
            elif event == "View Logs":
                self._show_logs_window()
            
            elif event == "Settings":
                self._show_settings_window()
        
        self.window.close()

    async def _handle_task_submission(self, task: str, values: Dict) -> None:
        """
        Handle task submission event.
        """
        self.update_status(f"Processing: {task[:50]}...")
        
        if self.app:
            try:
                result = await self.app.process_task(task)
                self.update_status(f"✓ Task completed: {result}")
            except Exception as e:
                self.update_status(f"✗ Task failed: {str(e)}")

    def _show_logs_window(self) -> None:
        """Show detailed logs window"""
        if self.app:
            logs = self.app.audit_log.get_log_summary(limit=100)
            log_text = "\n".join([f"[{log['timestamp']}] {log['action_type']}: {log['description']}" for log in logs])
            
            layout = [
                [sg.Multiline(log_text, size=(80, 20), disabled=True)],
                [sg.Button("Close")]
            ]
            
            window = sg.Window("Audit Log", layout)
            while True:
                event, _ = window.read()
                if event == sg.WINDOW_CLOSED or event == "Close":
                    break
            window.close()

    def _show_settings_window(self) -> None:
        """Show settings window"""
        layout = [
            [sg.Text("LLM Provider:"), sg.Combo(["Ollama", "OpenAI"], key="-LLM_PROVIDER-")],
            [sg.Text("Ollama Host:"), sg.Input(key="-OLLAMA_HOST-", default_text="http://localhost:11434")],
            [sg.Text("Ollama Model:"), sg.Input(key="-OLLAMA_MODEL-", default_text="mistral")],
            [sg.Button("Save"), sg.Button("Cancel")]
        ]
        
        window = sg.Window("Settings", layout)
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == "Cancel":
                break
            elif event == "Save":
                if self.app:
                    self.app.settings.set("llm.primary_provider", values["-LLM_PROVIDER-"].lower())
                    self.app.settings.set("llm.ollama.host", values["-OLLAMA_HOST-"])
                    self.app.settings.set("llm.ollama.model", values["-OLLAMA_MODEL-"])
                sg.Popup("Settings saved!")
                break
        
        window.close()
