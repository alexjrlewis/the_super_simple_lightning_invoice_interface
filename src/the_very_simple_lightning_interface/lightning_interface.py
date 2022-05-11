"""Module containing the Interface class."""

from decimal import Decimal
import json
import os
from typing import Any, Dict, List, Optional
import pandas as pd
import paramiko


MEMO_MAX_BYTES = 639  # https://bitcoin.stackexchange.com/questions/85951/whats-the-maximum-size-of-the-memo-in-a-ln-payment-request
STATES = ["OPEN", "SETTLED", "CANCELED", "ACCEPTED", "UNKNOWN"]
COLUMN_TO_DTYPE = {
    "memo": str,
    "r_preimage": str,
    "r_hash": str,
    "value": Decimal,
    "value_msat": Decimal,
    "settled": bool,
    "creation_date": int,
    "settle_date": int,
    "payment_request": str,
    "description_hash": str,
    "expiry": int,
    "fallback_addr": str,  # on-chain Bitcoin address in case.
    "cltv_expiry": int,
    "route_hints": str,
    "private": bool,
    "add_index": int,
    "settle_index": int,
    "amt_paid": Decimal,
    "amt_paid_sat": Decimal,
    "amt_paid_msat": Decimal,
    "state": str,
    "htlcs": str,
    "features": str,
    "is_keysend": bool,
    "payment_addr": str,
    "is_amp": bool,
    "amp_invoice_state": str,
}


def currency_to_msats(amount: Decimal, curreny: str = "GBP"):
    pass


def rate_to_msats(amount: Decimal, unit: str = "GB", rate: Decimal = Decimal()):
    pass


def clip_invoice_memo(memo: str) -> str:
    """Clips the memo such that it is within the MEMO_MAX_BYTES size.

    Args:
        memo: The memo to clip.
    Returns:
        The clipped memo such that its size is less than the MEMO_MAX_BYTES.
    """
    if len(memo.encode("utf-8")) > MEMO_MAX_BYTES:
        _memo = ""
        for i, c in enumerate(memo):
            if len((_memo + c).encode("utf-8")) < MEMO_MAX_BYTES:
                _memo += c
        return _memo
    return memo


def get_ssh_client(
    hostname: str, username: str, password: str
) -> paramiko.client.SSHClient:
    """Returns a connection to an SSH client

    Args:
        hostname: The hostname of the client.
        username: The username of the client.
        password: The password of the client.
    Returns:
        An SSH connection given the above credentials.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, username=username, password=password)
    return ssh_client


class InvoiceInterface:
    """Class providing a connection an interface to a lightning node via and SSH client.

    Attributes:
        username: The username of the node.
        ssh_client: A connected SSH client.
    """

    def __init__(self, hostname: str, username: str, password: str):
        """Initializes a new instance.

        Args:
            hostname:
            username:
            password:
        """
        self.username = username
        self.ssh_client = get_ssh_client(hostname, username, password)

    def _exec_command(self, command: str) -> Optional[Dict[str, str]]:
        """Executes a lighting command on the SSH client.

        Args:
            command: The command to execute, which must return valid JSON response.
        Returns:
            A JSON response of the lightning command or None.
        """
        # command = f"{self.username}/bin/lncli {command}"
        command = f"docker exec lnd lncli {command}"
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        stdin.close()
        lines = stdout.readlines()
        if len(lines) == 1:
            return lines[0]
        else:
            s = (
                "".join(lines).strip().replace("'", '"')
            )  # https://stackoverflow.com/questions/39491420/python-jsonexpecting-property-name-enclosed-in-double-quotes
            data = json.loads(s)
            return data

    def add_invoice(
        self, amount_sats: Decimal, memo: str = "", expiry_time: int = 300
    ) -> pd.Series:
        """Adds a lightning invoice and returns it as a series.

        Args:
            amount_sats: The amount in satoshis of the invoice.
            memo: The memo, i.e. description, of the invoice.
            expiry_time: How long the invoice lasts, in seconds.
        Returns:
            A series containing the invoice.
        """
        amount_msat = round(
            amount_sats * 1e3
        )  # convert satoshi amount to milli satoshis.
        command = f'addinvoice --amt_msat {amount_msat} --memo "{clip_invoice_memo(memo)}" --expiry {expiry_time}'
        data = self._exec_command(command)
        s = pd.Series(data)
        return s

    def get_invoice(self, r_hash: str) -> pd.Series:
        """Adds a lightning invoice and returns it as a series.

        Args:
            r_hash:
        Returns:
            
        """
        command = f"lookupinvoice {r_hash}"
        data = self._exec_command(command)
        invoice = pd.Series(data)
        return invoice

    def get_invoice_state(self, r_hash: str) -> str:
        """Adds a lightning invoice and returns it as a series.

        Args:
            r_hash:
        Returns:
            
        """
        invoice = self.get_invoice(r_hash)
        return invoice.state
