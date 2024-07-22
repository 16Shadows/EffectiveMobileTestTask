from __future__ import annotations

from typing import Self
from .core import MenuBase, MenuEntryBase, MenuHostBase

class SimpleConsoleMenuHost(MenuHostBase):
    """Реализация MenuHost, выводящая пункты меню построчно в консоль и предлагающая пользователю ввести номер пункта."""
    def run(self: Self, enterAt: MenuBase | None = None) -> None:
        if enterAt is not None:
            self.menuStack.clear()
            self.push(enterAt)
        
        while len(self.menuStack) > 0:
            currentMenu : MenuBase = self.current()
            currentMenuEntries : list[MenuEntryBase] = currentMenu.entries

            while True:
                print()
                print(currentMenu.text)
                for i in range(0, len(currentMenuEntries)):
                    print(i+1, ". ", currentMenuEntries[i].text)
                try:
                    user_input = input("Введите номер пункта: ")
                    option = int(user_input)
                    if option < 1 or option > len(currentMenuEntries):
                        raise ValueError
                except ValueError:
                    print(user_input, " - некорректный номер пункта.") # type: ignore
                    continue
                currentMenuEntries[option - 1].on_selected(self)
                break