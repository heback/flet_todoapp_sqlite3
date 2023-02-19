from flet import *
from datetime import datetime
import sqlite3


class Database:

    @staticmethod
    def connectToDatabase():
        try:
            db = sqlite3.connect('todo.db')
            c = db.cursor()
            c.execute(f'CREATE TABLE IF NOT EXISTS tasks '
                      f'(id INTEGER PRIMARY KEY,'
                      f'task VARCHAR(255) NOT NULL,'
                      f'date VARCHAR(255) NOT NULL)')
            return db
        except Exception as e:
            print(e)

    def readDatabase(db):
        c = db.cursor()
        c.execute('SELECT id, task, date FROM tasks')
        res = c.fetchall()
        return res

    def insertDatabase(db, values):
        c = db.cursor()
        c.execute('INSERT INTO tasks (task, date) VALUES (?, ?)', values)
        db.commit()
        return c.lastrowid

    def deleteDatabase(db, value):
        c = db.cursor()
        c.execute('DELETE FROM tasks WHERE id=?', value)
        db.commit()

    def updateDatabase(db, values):
        c = db.cursor()
        c.execute('UPDATE tasks SET task=? WHERE id=?', values)
        db.commit()



class FormContainer(UserControl):
    def __init__(self, func):
        self.func = func
        super().__init__()

    def build(self):
        return Container(
            width=280,
            height=80,
            bgcolor='bluegrey500',
            opacity=0,
            border_radius=40,
            margin=margin.only(left=-20, right=-20),
            animate=animation.Animation(400, 'decelerate'),
            animate_opacity=200,
            padding=padding.only(top=45, bottom=45),
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    TextField(
                        height=48,
                        width=255,
                        filled=True,
                        text_size=12,
                        color=colors.BLACK,
                        border_color='transparent',
                        hint_text='Description...',
                        hint_style=TextStyle(
                            size=11,
                            color='black'
                        )
                    ),
                    IconButton(
                        content=Text('Add Task', color=colors.WHITE),
                        width=180,
                        height=44,
                        on_click=self.func,
                        style=ButtonStyle(
                            color={"": colors.WHITE, "selected": colors.AMBER},
                            bgcolor={"": 'black'},
                            shape={"": RoundedRectangleBorder(radius=8)},
                        )
                    )
                ]
            )

        )


class CreateTask(UserControl):
    def __init__(self, task: str, date: str, func1, func2, id = None):
        self.id = id
        self.task = task
        self.date = date
        self.func1 = func1
        self.func2 = func2
        super().__init__()

    def task_delete_edit(self, name, color, func):
        return IconButton(
            icon=name,
            width=30,
            icon_size=18,
            opacity=0,
            icon_color=color,
            animate_opacity=200,
            on_click=lambda e: func(self.get_container_instance())
        )

    def get_container_instance(self):
        return self

    def show_icons(self, e):
        print(e)
        if e.data == 'true':
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity
            ) = (1, 1)
            e.control.content.update()
        else:
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity
            ) = (0, 0)
            e.control.content.update()

    def build(self):
        return Container(
            width=280,
            height=60,
            border=border.all(0.85, colors.WHITE54),
            border_radius=8,
            on_hover=lambda e: self.show_icons(e),
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=10,
            content=Row(
                spacing=1,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(self.task, size=10, color=colors.WHITE),
                            Text(self.date, size=9, color=colors.WHITE54),
                        ]
                    ),
                    Row(
                        spacing=0,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            self.task_delete_edit(
                                icons.DELETE_ROUNDED,
                                colors.RED_500,
                                self.func1
                            ),
                            self.task_delete_edit(
                                icons.EDIT_ROUNDED,
                                colors.WHITE70,
                                self.func2
                            )
                        ]
                    )

                ]
            )

        )


def main(page: Page):
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'

    def add_task_to_screen(e):
        dateTime = datetime.now().strftime('%b %d, %Y %I:%M')

        db = Database.connectToDatabase()

        if form.content.controls[0].value:

            id = Database.insertDatabase(db, (form.content.controls[0].value, dateTime))
            db.close()

            _main_column_.controls.append(
                CreateTask(
                    form.content.controls[0].value,
                    dateTime,
                    delete_func,
                    update_func,
                    id
                )
            )
            _main_column_.update()
            create_to_do_task(e)
        else:
            db.close()

    def delete_func(e):
        db = Database.connectToDatabase()
        Database.deleteDatabase(db, e.id)
        _main_column_.controls.remove(e)
        _main_column_.update()

    def update_func(e):
        form.height, form.opacity = 200, 1
        (
            form.content.controls[0].value,
            form.content.controls[1].content.value,
            form.content.controls[1].on_click
        ) = (
            e.controls[0].content.controls[0].controls[0].value,
            'Update',
            lambda _: finalize_update(e)
        )
        form.update()


    def finalize_update(e):
        e.controls[0].content.controls[0].controls[0].value = form.content.controls[0].value
        e.controls[0].content.update()
        create_to_do_task(e)

    def create_to_do_task(e):
        if form.height != 200:
            form.height = 200
            form.opacity = 1
            form.update()
        else:
            form.height = 80
            form.opacity = 0
            form.content.controls[0].value = None
            form.content.controls[1].content.value = 'Add Task'
            form.content.controls[1].on_click = lambda e: add_task_to_screen(e)
            form.update()

    _main_column_ = Column(
        scroll='hidden',
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Text(
                        'To-Do Items',
                        size=18,
                        color='white',
                        weight='bold'
                    ),
                    IconButton(
                        icons.ADD_CIRCLE_ROUNDED,
                        icon_size=18,
                        style=ButtonStyle(
                            color='white',
                        ),
                        on_click=lambda e: create_to_do_task(e),
                    ),


                ]
            ),
            Divider(height=8, color='white24')
        ]
    )

    page.add(
        Container(
            width=800,
            height=700,
            margin=-10,
            bgcolor=colors.BLUE_GREY_900,
            alignment=alignment.center,
            content=Row(
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Container(
                        width=280,
                        height=600,
                        bgcolor='#0f0f0f',
                        border_radius=40,
                        border=border.all(0.5, 'white'),
                        padding=padding.only(top=35, left=20, right=20),
                        clip_behavior=ClipBehavior.HARD_EDGE,
                        content=Column(
                            alignment=MainAxisAlignment.CENTER,
                            expand=True,
                            controls=[
                                _main_column_,
                                FormContainer(lambda e: add_task_to_screen(e)),
                            ]

                        )
                    )
                ]
            )
        )
    )

    page.update()

    form = page.controls[0].content.controls[0].content.controls[1].controls[0]

    db = Database.connectToDatabase()

    for task in Database.readDatabase(db):
        _main_column_.controls.append(
            CreateTask(
                task[0],
                task[1],
                delete_func,
                update_func,
                task[2]
            )
        )
    _main_column_.update()



if __name__ == '__main__':
    flet.app(target=main)