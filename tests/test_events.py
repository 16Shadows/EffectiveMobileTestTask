import unittest
from modules.events import Event, WeakSubscriber
from typing import Self

class EventTestSuite(unittest.TestCase):
    def test_event_strong(self: Self):
        cnt : int = 0

        def inc_cnt():
            nonlocal cnt
            cnt += 1

        e = Event[()]()

        #Т.к. Event должен держать сильные ссылки, все 3 метода должны выжить
        e += lambda: inc_cnt()
        e += lambda: inc_cnt()
        e += lambda: inc_cnt()

        e()

        self.assertEqual(cnt, 3)
        
    def test_event_weak(self: Self):
        cnt : int = 0

        class Inc:
            def inc_cnt(self):
                nonlocal cnt
                cnt += 1

        e = Event[()]()

        inst1 = Inc()
        inst2 = Inc()

        e += inst1.inc_cnt
        e += WeakSubscriber(inst2.inc_cnt)

        e()

        self.assertEqual(cnt, 2)

        #Т.к. WeakSubscriber не должен держать сильных ссылок, inst2 и связанный метод должны быть уничтожены
        inst1 = None
        inst2 = None

        e()

        self.assertEqual(cnt, 3)