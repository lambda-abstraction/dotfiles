from datetime import datetime
from psutil import cpu_percent, virtual_memory
from ignis.widgets import Widget
from ignis.app import IgnisApp
from ignis.utils import Utils
from ignis.services.audio import AudioService
from ignis.services.mpris import MprisService, MprisPlayer
from ignis.services.hyprland import HyprlandService

app = IgnisApp.get_default()
app.apply_css(Utils.get_current_dir() + "/style.scss")

audio = AudioService.get_default()
mpris = MprisService.get_default()
hyprland = HyprlandService.get_default()

def update_clock(clock_label: Widget.Label) -> None:
    time = datetime.now().strftime("(%b %d %H:%M:%S)")
    clock_label.label = time

def clock() -> Widget.Label:
    clock_label = Widget.Label()
    Utils.Poll(1000, lambda x: update_clock(clock_label))
    return clock_label

def update_resources(resources_label: Widget.Label) -> None:
    resources = f"[CPU: {cpu_percent()}%] [RAM: {virtual_memory().percent}%]"
    resources_label.label = resources 

def resources() -> Widget.Label:
    resources_label = Widget.Label()
    Utils.Poll(1000, lambda x: update_resources(resources_label))
    return resources_label

def window_title():
    return Widget.Label(
        max_width_chars=60,
        label=hyprland.bind(
            "active_window",
            transform=lambda value: value.get(
                "title",
                "",
            ).ljust(100),
        ),
    )


def mpris_title(player: MprisPlayer) -> Widget.Box:
    return Widget.Box(
        spacing=10,
        setup=lambda self: player.connect(
            "closed",
            lambda x: self.unparent(),
        ),
        child=[
            Widget.Icon(image="audio-x-generic-symbolic"),
            Widget.Label(
                max_width_chars=20,
                label=player.bind("title"),
            ),
        ]
    )

def media() -> Widget.Box:
    return Widget.Box(
        spacing=10,
        child=[
            Widget.Label(
                label="No media players",
                visible=mpris.bind("players", lambda value: len(value) == 0),
            ),
        ],
        setup=lambda self: mpris.connect(
            "player-added", lambda x, player: self.append(mpris_title(player))
        ),
    )

def speaker_volume() -> Widget.Box:
    return Widget.Box(
        child=[
            Widget.Icon(image=audio.speaker.bind("icon_name")),
            Widget.Label(label=audio.speaker.bind("volume", transform=lambda value: f"{value}%".ljust(4))),
        ],
    )

def speaker_slider() -> Widget.Scale:
    return Widget.Scale(
        min=0,
        max=200,
        step=1,
        value=audio.speaker.bind("volume"),
        on_change=lambda x: audio.speaker.set_volume(x.value),
        css_classes=["volume-slider"],
    )

def workspace_button(workspace: dict) -> Widget.Button:
    widget = Widget.Button(
        css_classes=["workspace"],
        on_click=lambda x, id=workspace["id"]: hyprland.switch_to_workspace(id),
        child=Widget.Label(label=str(workspace["id"])),
    )
    if workspace["id"] == hyprland.active_workspace["id"]:
        widget.add_css_class("active")

    return widget

def scroll_workspace(offset: int) -> None:
    current = hyprland.active_workspace["id"]
    new = (current + offset) % 10
    hyprland.switch_to_workspace(new)

def workspaces() -> Widget.EventBox:
    return Widget.EventBox(
        on_scroll_up=lambda x: scroll_workspace(-1),
        on_scroll_down=lambda x: scroll_workspace(+1),
        css_classes=["workspaces"],
        spacing=5,
        child=hyprland.bind(
            "workspaces",
            transform=lambda value: [workspace_button(i) for i in value],
        ),
    )

Widget.Window(
    namespace="bar",
    anchor=["left", "top", "right"],
    exclusivity="exclusive",
    child=Widget.CenterBox(
        vertical=False,
        start_widget=Widget.Box(
            spacing=10,
            child=[
                workspaces(),
                window_title(),
            ],
        ),
        center_widget=Widget.Box(
            spacing=20,
            child=[
                clock(),
                speaker_volume(),
                speaker_slider(),
            ],
        ),
        end_widget=Widget.Box(
            spacing=10,
            child=[
                media(),
                resources(),
            ],
        ),
    ),
)
