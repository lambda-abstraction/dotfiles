from datetime import datetime
from ignis.widgets import Widget
from ignis.app import IgnisApp
from ignis.utils import Utils

app = IgnisApp.get_default()
app.apply_css(Utils.get_current_dir() + "/style.scss")

def update_label(clock_label: Widget.Label) -> None:
    text = datetime.now().strftime("%b %d %H:%M:%S")
    clock_label.label = text

def clock() -> Widget.Label:
    clock_label = Widget.Label()
    Utils.Poll(1000, lambda x: update_label(clock_label))
    return clock_label

Widget.Window(
    namespace="bar",
    anchor=["left", "top", "right"],
    exclusivity="exclusive",
    child=Widget.CenterBox(
        vertical=False,
        center_widget=clock(),
    ),
)
