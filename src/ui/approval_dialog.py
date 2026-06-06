"""Approval Dialog - Visual approval interface"""

import logging
import PySimpleGUI as sg
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ApprovalDialog:
    """
    Visual dialog for user approval of agent actions.
    Shows:
    - What action is requested
    - Why it's needed
    - What will change
    - Approve/Reject buttons
    """

    @staticmethod
    def show_approval_dialog(
        title: str,
        description: str,
        details: Dict[str, Any],
        action_type: str = "generic"
    ) -> bool:
        """
        Show approval dialog and return user decision.
        
        Returns:
            True if approved, False if rejected
        """
        # Build details display
        details_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
        
        layout = [
            [sg.Text(title, font=("Arial", 14, "bold"))],
            [sg.Text(f"Action Type: {action_type}", text_color="blue")],
            [sg.HorizontalSeparator()],
            [sg.Text("Description:")],
            [sg.Multiline(description, size=(60, 4), disabled=True)],
            [sg.Text("Details:")],
            [sg.Multiline(details_text, size=(60, 6), disabled=True)],
            [sg.HorizontalSeparator()],
            [
                sg.Button("✓ Approve", button_color=("white", "green"), size=(15, 1)),
                sg.Push(),
                sg.Button("✗ Reject", button_color=("white", "red"), size=(15, 1))
            ]
        ]
        
        window = sg.Window(
            "Approval Required",
            layout,
            modal=True,
            finalize=True,
            keep_on_top=True
        )
        
        result = None
        while True:
            event, values = window.read()
            
            if event == sg.WINDOW_CLOSED:
                result = False
                break
            elif event == "✓ Approve":
                result = True
                break
            elif event == "✗ Reject":
                result = False
                break
        
        window.close()
        logger.info(f"Approval dialog result: {result}")
        return result
