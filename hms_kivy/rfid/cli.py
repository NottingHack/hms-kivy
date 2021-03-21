# -*- coding: utf-8 -*-
""" HMS Kiosk (RFID CLI module)

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
import typer
import sys
import socket
import json


app = typer.Typer()
DEFAULT_PORT = 7861
state = {"port": DEFAULT_PORT}


@app.callback()
def main(
    port: int = typer.Option(
        DEFAULT_PORT, "--port", "-p", help="UDP port to broadcast on"
    )
):
    """
    RFID over UDP helper
    """
    if port != DEFAULT_PORT:
        typer.echo(f"Will use UDP port {port}")
        state["port"] = port


@app.command()
def present(uid: str = typer.Argument(..., help="uid to send")):
    """
    Present an RFID card with the given UID to the reader
    """
    typer.echo(f"Presenting RFID {uid}")

    packet = {"uid": uid}

    if not send_packet(json.dumps(packet)):
        raise typer.Exit()


@app.command()
def remove():
    """
    Remove the RFID card from the reader
    """
    typer.echo("Removing RFID")
    packet = {"uid": ""}

    if not send_packet(json.dumps(packet)):
        raise typer.Exit()


def send_packet(json_packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        sock.sendto(json_packet.encode(), ("localhost", state["port"]))
    except socket.error as msg:
        typer.secho(
            f"Failed to send via localhost, Error code : {msg.errno} Message: {msg.strerror}",
            err=True,
            fg=typer.colors.WHITE,
            bg=typer.colors.RED,
        )
        sock.close()

        return False
    else:
        typer.secho("Sent via localhost", fg=typer.colors.GREEN)

    sock.close()

    return True
