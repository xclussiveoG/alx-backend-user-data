#!/usr/bin/env python3
"""
    RedactingFormatter
    """
    import csv
    import logging
    import os
    import re
    from typing import List
    import mysql.connector

    PII_FIELDS = ("name", "email", "phone", "ssn", "password")
