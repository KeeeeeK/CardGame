"""
Иерархия прав:
    ClientAction, Action
    ClientAnimation <- тянет лишь индексирование методов из Animation на этапе тестирования
    ---
    TaskManager
    Card
    Container
    Player
    Game
    Rules
    Animation, ServerAnimation
    GlobalAnimation
    ServerAction

Снизу вверх растёт зависимость.
"""
