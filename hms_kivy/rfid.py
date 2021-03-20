#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" HMS Kiosk (RFID module)

    Requirements (pi only)
    pi-rc522 (https://github.com/kevinvalk/pi-rc522.git)

    Author: Matt Lloyd
    Copyright (c) 2020 Nottingham Hackspace

    The MIT License (MIT)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
import time
import queue
import threading
import socket
import select
import json
from binascii import hexlify

# from kivy.config import Config
from kivy.logger import Logger


class RFID:
    _reader = False
    _listenPort = 7861
    _UDP_listen_timeout = 2  # timeout for UDP listen
    _readTimeout = 10  # allow read of same card after 10 seconds

    def __init__(self):
        self.t_RFID_stop = threading.Event()
        self.q_RFID = queue.Queue()
        try:
            global pirc522
            import pirc522 as pirc522

            self._reader = pirc522.RFID(pin_irq=None, antenna_gain=7)
            Logger.debug("RFID: using pirc522")
        except ImportError:
            Logger.debug(
                "RFID: Error importing pirc522. Will listen for UDP on {}".format(
                    self._listenPort
                )
            )
        except:
            Logger.debug(
                "RFID: Error importing pirc522 Will listen for UDP on {}".format(
                    self._listenPort
                )
            )

    def start_RFID_read(self):
        if self._reader:
            self.t_thread = threading.Thread(
                name="tRC522read", target=self._rc522_thread
            )
        else:
            self.t_thread = threading.Thread(name="tUDPListen", target=self._udpThread)

        try:
            self.t_thread.start()
        except:
            Logger.debug("RFID: Failed to start thread: {}".format(self.t_thread.name))

    def stop_RFID_read(self):
        Logger.debug("RFID: Stopping thread")
        self.t_RFID_stop.set()

    def clear_queue(self):
        with self.q_RFID.mutex:
            self.q_RFID.queue.clear()

    def _rc522_thread(self):
        """pi-rc522 Read thread
        We read for new RFID uid's and post to q_RFID
        """
        Logger.debug("tRC522read: Thread started")
        last_uid = None
        last_read_time = 0
        while not self.t_RFID_stop.is_set():
            # clear last read if it was a while ago
            if ((time.time() - last_read_time)) > self._readTimeout:
                last_read_time = time.time()
                last_uid = None

            uid = self._reader.read_id()
            if uid is not None:
                uid_number = hexlify(bytearray(uid))
                if last_uid != uid_number:
                    last_uid = uid_number
                    try:
                        self.q_RFID.put_nowait(uid_number)
                    except queue.Full:
                        Logger.debug(
                            "tRC522read: Failed to put {} on q_RFID as it's full".format(
                                uid_number
                            )
                        )

            self.t_RFID_stop.wait(0.1)
        Logger.debug("tRC522read: Thread stopped")

    def _udpThread(self):
        """UDP Read thread
        We listen via UDP for a new UID and post to q_RFID
        """
        Logger.debug("tUDPListen: Thread started")
        last_uid = None

        try:
            UDP_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            Logger.debug("tUDPListen: Failed to create socket, Exiting")
            return

        UDP_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        UDP_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            UDP_listen_socket.bind(("", self._listenPort))
        except socket.error:
            Logger.debug("tUDPListen: Failed to bind port, Exiting")
            return

        UDP_listen_socket.setblocking(0)

        Logger.debug("tUDPListen: listening")
        while not self.t_RFID_stop.is_set():
            datawaiting = select.select(
                [UDP_listen_socket], [], [], self._UDP_listen_timeout
            )
            if datawaiting[0]:
                (uid_number, address) = UDP_listen_socket.recvfrom(8192)
                Logger.debug(
                    "tUDPListen: Received: {} From: {}".format(uid_number, address)
                )

                # clear last read if it was a while ago
                if (time.time() - last_read_time) > self._readTimeout:
                    last_read_time = time.time()
                    last_uid = None

                if last_uid != uid_number:
                    last_uid = uid_number
                    try:
                        self.q_RFID.put_nowait(uid_number)
                    except queue.Full:
                        Logger.debug(
                            "{}: Failed to put {} on q_RFID as it's full".format(
                                self.t_thread.name, uid_number
                            )
                        )

        Logger.debug("tUDPListen: Thread stopping")
        try:
            UDP_listen_socket.close()
        except socket.error:
            Logger.debug("tUDPListen: Failed to close socket")
        Logger.debug("tUDPListen: Thread stopped")
        return
