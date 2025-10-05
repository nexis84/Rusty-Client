# widget_handler.py

from enum import Enum

# --- PyQt6 Imports ---
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QPoint, QRect, QEvent

# --- Constants ---
RESIZE_MARGIN = 8 # Pixels for resize handles

# --- Enums ---
class Handle(Enum):
    NONE = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4
    TOP_LEFT = 5
    TOP_RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_RIGHT = 8
    BODY = 9 # For moving

# --- Widget Drag/Resize Handler Class ---
class WidgetDragHandler(QObject):
    """Handles mouse events for draggable/resizable widgets in Adjust Layout Mode."""
    geometry_changed = pyqtSignal(QWidget, str) # Emits (widget, "x,y,w,h")

    def __init__(self, parent_app):
        """
        Args:
            parent_app: The main GiveawayApp instance.
        """
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.target_widget = None     # The widget currently being dragged/resized
        self.action_mode = Handle.NONE # What action is being performed (move/resize handle)
        self.offset = QPoint()        # Mouse offset from widget corner during drag/resize start
        self.start_geometry = QRect() # Widget geometry at drag/resize start
        self.widgets = []             # List of widgets managed by this handler
        self.current_hover_handle = Handle.NONE # Which handle the mouse is currently over

    def add_widget(self, widget):
        """Adds a widget to be managed by the handler."""
        if widget not in self.widgets:
            widget.installEventFilter(self)
            widget.setAttribute(Qt.WidgetAttribute.WA_Hover, True) # Enable hover events
            self.widgets.append(widget)
            print(f"DragHandler: Filter installed on {widget.objectName() or widget}")

    def remove_widget(self, widget):
        """Removes a widget from being managed."""
        if widget in self.widgets:
            try:
                widget.removeEventFilter(self)
            except RuntimeError: # Can happen if widget is deleted before filter removal
                pass
            self.widgets.remove(widget)
            print(f"DragHandler: Filter removed from {widget.objectName() or widget}")

    def _get_handle_at(self, widget, pos: QPoint) -> Handle:
        """Determines which handle (if any) is at the given position within the widget."""
        r = widget.rect()
        m = RESIZE_MARGIN

        on_top = abs(pos.y() - r.top()) < m
        on_bottom = abs(pos.y() - r.bottom()) < m
        on_left = abs(pos.x() - r.left()) < m
        on_right = abs(pos.x() - r.right()) < m

        # Check corners first
        if on_top and on_left: return Handle.TOP_LEFT
        if on_top and on_right: return Handle.TOP_RIGHT
        if on_bottom and on_left: return Handle.BOTTOM_LEFT
        if on_bottom and on_right: return Handle.BOTTOM_RIGHT
        # Check edges
        if on_top: return Handle.TOP
        if on_bottom: return Handle.BOTTOM
        if on_left: return Handle.LEFT
        if on_right: return Handle.RIGHT
        # Check body for moving
        if r.contains(pos): return Handle.BODY

        return Handle.NONE

    def _update_cursor(self, widget: QWidget, handle: Handle):
        """Sets the mouse cursor shape based on the handle."""
        cursor_shape = Qt.CursorShape.ArrowCursor # Default cursor if locked

        # <<< Check Lock State >>>
        is_locked = self.parent_app.config.get("ui_locked", True)
        if not is_locked: # Only show resize/move cursors if unlocked
            if handle == Handle.TOP or handle == Handle.BOTTOM:
                cursor_shape = Qt.CursorShape.SizeVerCursor
            elif handle == Handle.LEFT or handle == Handle.RIGHT:
                cursor_shape = Qt.CursorShape.SizeHorCursor
            elif handle == Handle.TOP_LEFT or handle == Handle.BOTTOM_RIGHT:
                cursor_shape = Qt.CursorShape.SizeFDiagCursor
            elif handle == Handle.TOP_RIGHT or handle == Handle.BOTTOM_LEFT:
                cursor_shape = Qt.CursorShape.SizeBDiagCursor
            elif handle == Handle.BODY:
                cursor_shape = Qt.CursorShape.SizeAllCursor # Move cursor

        widget.setCursor(cursor_shape)

    def eventFilter(self, source_widget: QObject, event: QEvent) -> bool:
        """Filters mouse events for managed widgets."""
        # --- Check if Customisable UI Mode is enabled ---
        is_custom_mode = self.parent_app.config.get("customisable_ui_enabled", False)
        if not is_custom_mode:
            # If mode disabled, ensure cursor is reset and ignore events
            if source_widget in self.widgets and isinstance(source_widget, QWidget):
                 if source_widget.cursor().shape() != Qt.CursorShape.ArrowCursor:
                      source_widget.unsetCursor()
                 # Ensure border class is removed if mode is off
                 current_class = source_widget.property("class")
                 if current_class and "adjustable-widget-active" in current_class:
                     new_class = current_class.replace(" adjustable-widget-active", "").strip()
                     source_widget.setProperty("class", new_class if new_class else None)
                     source_widget.style().unpolish(source_widget)
                     source_widget.style().polish(source_widget)

            self.current_hover_handle = Handle.NONE
            return super().eventFilter(source_widget, event) # Pass event through

        # --- Mode is enabled, proceed with handling ---
        if source_widget not in self.widgets or not isinstance(source_widget, QWidget):
            return super().eventFilter(source_widget, event)

        # <<< Check Lock State >>>
        is_locked = self.parent_app.config.get("ui_locked", True)

        # Safely get event position
        event_pos = QPoint()
        if hasattr(event, 'position'): # For Hover events
            event_pos = event.position().toPoint()
        elif hasattr(event, 'pos'): # For MouseButton events
             event_pos = event.pos()

        # --- Event Handling ---
        event_type = event.type()

        if event_type == QEvent.Type.HoverMove:
            if self.action_mode == Handle.NONE: # Only update cursor if not currently dragging/resizing
                handle = Handle.NONE
                if not is_locked: # Only detect handles if unlocked
                    handle = self._get_handle_at(source_widget, event_pos)

                if handle != self.current_hover_handle:
                    self._update_cursor(source_widget, handle)
                    self.current_hover_handle = handle
            return True # Consume hover move event

        elif event_type == QEvent.Type.HoverLeave:
            if self.action_mode == Handle.NONE: # Only reset cursor if not dragging
                source_widget.unsetCursor()
                self.current_hover_handle = Handle.NONE
            return True # Consume hover leave event

        elif event_type == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton and not is_locked: # <<< Check lock state here >>>
                self.action_mode = self._get_handle_at(source_widget, event_pos)
                if self.action_mode != Handle.NONE:
                    self.target_widget = source_widget
                    self.start_geometry = self.target_widget.geometry()
                    self.offset = event.globalPosition().toPoint() - self.start_geometry.topLeft()
                    self.target_widget.raise_()
                    self._update_cursor(self.target_widget, self.action_mode) # Cursor already reflects unlocked state
                    return True # Consume press event if handle is grabbed and unlocked
            # If locked or not left button or no handle, let event propagate
            return False

        elif event_type == QEvent.Type.MouseMove:
            # <<< Check lock state: Should not happen if press was blocked, but good safety check >>>
            if self.action_mode != Handle.NONE and self.target_widget and not is_locked:
                new_global_pos = event.globalPosition().toPoint()
                new_pos_based_on_offset = new_global_pos - self.offset
                new_geo = QRect(self.start_geometry)

                min_w = max(self.target_widget.minimumSizeHint().width(), 50)
                min_h = max(self.target_widget.minimumSizeHint().height(), 30)

                # --- Calculate new geometry based on action mode --- (Logic unchanged here)
                if self.action_mode == Handle.BODY:
                    new_geo.moveTo(new_pos_based_on_offset) # Move uses offset directly
                elif self.action_mode == Handle.RIGHT:
                     delta_x = new_global_pos.x() - (self.parent_app.mapToGlobal(self.start_geometry.topRight()).x())
                     new_geo.setWidth(max(min_w, self.start_geometry.width() + delta_x))
                     new_geo.moveTopLeft(self.start_geometry.topLeft())
                elif self.action_mode == Handle.LEFT:
                    delta_x = new_global_pos.x() - (self.parent_app.mapToGlobal(self.start_geometry.topLeft()).x())
                    new_right = self.start_geometry.right()
                    new_left = min(new_right - min_w, self.start_geometry.left() + delta_x)
                    new_geo.setLeft(new_left)
                    new_geo.moveTop(self.start_geometry.top())
                elif self.action_mode == Handle.BOTTOM:
                     delta_y = new_global_pos.y() - (self.parent_app.mapToGlobal(self.start_geometry.bottomLeft()).y())
                     new_geo.setHeight(max(min_h, self.start_geometry.height() + delta_y))
                     new_geo.moveTopLeft(self.start_geometry.topLeft())
                elif self.action_mode == Handle.TOP:
                    delta_y = new_global_pos.y() - (self.parent_app.mapToGlobal(self.start_geometry.topLeft()).y())
                    new_bottom = self.start_geometry.bottom()
                    new_top = min(new_bottom - min_h, self.start_geometry.top() + delta_y)
                    new_geo.setTop(new_top)
                    new_geo.moveLeft(self.start_geometry.left())
                elif self.action_mode == Handle.BOTTOM_RIGHT:
                    delta_x = new_global_pos.x() - (self.parent_app.mapToGlobal(self.start_geometry.topRight()).x())
                    delta_y = new_global_pos.y() - (self.parent_app.mapToGlobal(self.start_geometry.bottomLeft()).y())
                    new_geo.setWidth(max(min_w, self.start_geometry.width() + delta_x))
                    new_geo.setHeight(max(min_h, self.start_geometry.height() + delta_y))
                    new_geo.moveTopLeft(self.start_geometry.topLeft())
                elif self.action_mode == Handle.TOP_LEFT:
                    delta_x = new_global_pos.x() - (self.parent_app.mapToGlobal(self.start_geometry.topLeft()).x())
                    delta_y = new_global_pos.y() - (self.parent_app.mapToGlobal(self.start_geometry.topLeft()).y())
                    new_right = self.start_geometry.right()
                    new_bottom = self.start_geometry.bottom()
                    new_left = min(new_right - min_w, self.start_geometry.left() + delta_x)
                    new_top = min(new_bottom - min_h, self.start_geometry.top() + delta_y)
                    new_geo.setTopLeft(QPoint(new_left, new_top))
                elif self.action_mode == Handle.TOP_RIGHT:
                    delta_x = new_global_pos.x() - (self.parent_app.mapToGlobal(self.start_geometry.topRight()).x())
                    delta_y = new_global_pos.y() - (self.parent_app.mapToGlobal(self.start_geometry.topLeft()).y())
                    new_bottom = self.start_geometry.bottom()
                    new_width = max(min_w, self.start_geometry.width() + delta_x)
                    new_top = min(new_bottom - min_h, self.start_geometry.top() + delta_y)
                    new_geo.setTop(new_top)
                    new_geo.setWidth(new_width)
                    new_geo.moveLeft(self.start_geometry.left())
                elif self.action_mode == Handle.BOTTOM_LEFT:
                    delta_x = new_global_pos.x() - (self.parent_app.mapToGlobal(self.start_geometry.topLeft()).x())
                    delta_y = new_global_pos.y() - (self.parent_app.mapToGlobal(self.start_geometry.bottomLeft()).y())
                    new_right = self.start_geometry.right()
                    new_left = min(new_right - min_w, self.start_geometry.left() + delta_x)
                    new_height = max(min_h, self.start_geometry.height() + delta_y)
                    new_geo.setLeft(new_left)
                    new_geo.setHeight(new_height)
                    new_geo.moveTop(self.start_geometry.top())

                # Apply the calculated geometry
                self.target_widget.setGeometry(new_geo)

                # Force parent repaint
                parent = self.target_widget.parentWidget()
                if parent:
                    parent.update()

                return True # Consume move event during drag/resize
            # If locked or not dragging, let event propagate
            return False

        elif event_type == QEvent.Type.MouseButtonRelease:
            # We need to handle release even if locked, in case a drag was started before locking
            if event.button() == Qt.MouseButton.LeftButton and self.action_mode != Handle.NONE:
                current_action = self.action_mode
                self.action_mode = Handle.NONE # Reset action mode FIRST

                if self.target_widget:
                    # Update cursor based on final position and lock state
                    final_handle = Handle.NONE
                    if not is_locked: # Only detect handles if unlocked
                         final_handle = self._get_handle_at(self.target_widget, event_pos)
                    self._update_cursor(self.target_widget, final_handle) # Will set arrow if locked
                    self.current_hover_handle = final_handle

                    # Emit the final geometry only if we weren't locked during the action
                    if not is_locked:
                        geom = self.target_widget.geometry()
                        geo_str = f"{geom.x()},{geom.y()},{geom.width()},{geom.height()}"
                        self.geometry_changed.emit(self.target_widget, geo_str)
                        # print(f"Action End: {self.target_widget.objectName()} at {geo_str} (Mode: {current_action})") # Debug

                self.target_widget = None # Release target widget
                return True # Consume release event
            # If not left button release or not in action mode, let event propagate
            return False

        # Pass unhandled events to the original handler
        return super().eventFilter(source_widget, event)