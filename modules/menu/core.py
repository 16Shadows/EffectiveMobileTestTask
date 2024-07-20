from __future__ import annotations

from typing import Self
import abc

class MenuEntryBase(abc.ABC):
    """Базовый абстрактный класс пункта меню."""

    @property
    @abc.abstractmethod
    def text(self: Self) -> str:
        """Возвращает текст этого пункта меню"""
        pass

    @abc.abstractmethod
    def on_selected(self: Self, host: MenuHostBase) -> None:
        """Обработчик события выбора этого пункта меню.
        
        Аргументы:
        host : MenuHostBase -- контекст, в котором отображается меню.
        """
        pass

class MenuBase(abc.ABC):
    """Базовый абстрактный класс меню."""

    @property
    @abc.abstractmethod
    def text(self: Self) -> str:
        """Возвращает текст этого меню."""
        pass

    @property
    @abc.abstractmethod
    def entries(self: Self) -> list[MenuEntryBase]:
        """Возвращает пункты этого меню"""

class MenuHostBase(abc.ABC):
    """Базовый класс контекста отображения меню. Реализует логику перехода между меню и их отображения."""
    def __init__(self) -> None:
        self.menuStack : list[MenuBase] = []
    
    def push(self: Self, menu: MenuBase) -> None:
        """Добавить меню на вершину стека открытых меню. Меню на вершине стека отображается контекстом.
        
        menu : Menu -- меню для добавления.
        """
        self.menuStack.append(menu)

    def pop(self: Self) -> None:
        """Убрать меню с вершины стека открытых меню. Меню на вершине стека отображается контекстом."""
        self.menuStack.pop()

    def current(self: Self) -> MenuBase:
        """Получить текущее меню на вершине стека открытых меню."""
        return self.menuStack[-1]
    
    @abc.abstractmethod
    def run(self: Self, enterAt: MenuBase | None = None) -> None:
        """Начать отображение меню в текущем контексте.
        Этот метод блокирующий и завершится, когда последнее меню будет закрыто.
        
        menu : Menu | None -- меню, с которого нужно начать отображение.
                              Если меню указано, то текущей стек открытых меню будет очищен.
                              Если передано значение None, то будет открыто меню на вершине стека.
        """
        pass