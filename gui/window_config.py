import toga
from toga.style import Pack
from travertino.constants import COLUMN, ROW, CENTER
from config import WORKDIR_ROOT

class WindowConfig(toga.Window):
    def __init__(self):
        self.text_folder = toga.TextInput(placeholder='请选择配置保存目录...', readonly=True, style=Pack(width=300), )
        self.text_folder.value = WORKDIR_ROOT.resolve()
        basic_box = toga.Box(
            children=[
                # button_box,
                # self.label,
                toga.Label('请选择配置保存目录：'),
                self.text_folder,
                toga.Button('...', on_press=self.action_select_folder_dialog)
            ],
            style=Pack(
                direction=ROW,

                # align_items=CENTER,
                # margin=5,
            ),
        )

        container = toga.OptionContainer(
            content=[("基础配置", basic_box), ],
            style=Pack(flex=1)
        )

        button_box = toga.Box(children=[toga.Button('取消'), toga.Button('确定')], style=Pack(text_align='right', ))

        box = toga.Box(
            children=[
                container,
                button_box
            ],
            style=Pack(direction=COLUMN)
            # style=Pack(flex=1),
        )
        # container.current_tab = 1
        super(WindowConfig, self).__init__(title='aitrader 配置中心', size=(650, 480), resizable=False)
        self.content = box

    async def action_select_folder_dialog(self, widget):
        try:
            path_name = await self.dialog(
                toga.SelectFolderDialog(title="Select folder with Toga")
            )
            if path_name is not None:
                self.text_folder.value = f"{path_name}"
            else:
                self.text_folder.value = "No folder selected!"
        except ValueError:
            self.text_folder.value = "Folder select dialog was canceled"
