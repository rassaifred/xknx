import unittest
from unittest.mock import Mock
import asyncio
from xknx import XKNX, Sensor
from xknx.knx import Telegram, Address, TelegramType, DPTArray, DPTBinary

class TestSensor(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    #
    # STR FUNCTIONS
    #
    def test_str_array(self):
        xknx = XKNX(loop=self.loop)
        sensor = Sensor(
            xknx,
            'TestSensor',
            group_address='1/2/3')
        sensor.state = DPTArray((0x01, 0x02, 0x03))

        self.assertEqual(sensor.resolve_state(), "0x01,0x02,0x03")


    def test_str_binary(self):
        xknx = XKNX(loop=self.loop)
        sensor = Sensor(
            xknx,
            'TestSensor',
            group_address='1/2/3')
        sensor.state = DPTBinary(5)

        self.assertEqual(sensor.resolve_state(), "101")


    def test_str_scaling(self):
        xknx = XKNX(loop=self.loop)
        sensor = Sensor(
            xknx,
            'TestSensor',
            group_address='1/2/3',
            value_type="percent")
        sensor.state = DPTArray((0x40,))

        self.assertEqual(sensor.resolve_state(), "25")
        self.assertEqual(sensor.unit_of_measurement(), "%")


    #
    # SYNC
    #
    def test_sync(self):
        xknx = XKNX(loop=self.loop)
        sensor = Sensor(
            xknx,
            'TestSensor',
            group_address='1/2/3')

        self.loop.run_until_complete(asyncio.Task(sensor.sync(False)))

        self.assertEqual(xknx.telegrams.qsize(), 1)

        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(Address('1/2/3'), TelegramType.GROUP_READ))

    #
    # TEST PROCESS
    #
    def test_process(self):
        xknx = XKNX(loop=self.loop)
        sensor = Sensor(
            xknx,
            'TestSensor',
            group_address='1/2/3')

        telegram = Telegram(Address('1/2/3'))
        telegram.payload = DPTArray((0x01, 0x02, 0x03))
        sensor.process(telegram)

        self.assertEqual(sensor.state, DPTArray((0x01, 0x02, 0x03)))


    def test_process_callback(self):
        # pylint: disable=no-self-use
        xknx = XKNX(loop=self.loop)
        sensor = Sensor(
            xknx,
            'TestSensor',
            group_address='1/2/3')

        after_update_callback = Mock()
        sensor.register_device_updated_cb(after_update_callback)

        telegram = Telegram(Address('1/2/3'))
        telegram.payload = DPTArray((0x01, 0x02, 0x03))
        sensor.process(telegram)

        after_update_callback.assert_called_with(sensor)



SUITE = unittest.TestLoader().loadTestsFromTestCase(TestSensor)
unittest.TextTestRunner(verbosity=2).run(SUITE)